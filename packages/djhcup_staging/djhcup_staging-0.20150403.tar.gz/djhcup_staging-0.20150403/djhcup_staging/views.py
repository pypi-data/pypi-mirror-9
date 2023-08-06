# core Python packages
import datetime
import logging
import os
import sys


# third party packages
import pandas as pd
import pyhcup
import datetime


# django packages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.timezone import utc
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections as cnxns
from django.db import transaction as tx
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, TemplateView
from django.contrib import messages

# local project and app packages
import djhcup_staging
from djhcup_staging import tasks
from djhcup_staging.models import State, DataSource, FileType, File, Column, ImportQueue, ImportBatch, StagingTable, StagingBatch, StagingQueue, ReferenceColumn
from djhcup_staging.utils import misc, staging


# move these into the local namespace
DJHCUP_IMPORT_PATHS = settings.DJHCUP_IMPORT_PATHS


# kludge workaround--move to config later
DJHCUP_DB_ENTRY = 'djhcup'

# start a logger
logger = logging.getLogger('default')

class Index(TemplateView):
    template_name = 'stg_base.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Index, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['links'] = [
            {
                'display': 'Data source definitions',
                'href': reverse('ds_inv'),
            },
            {   
                'display': 'Files',
                'href': reverse('file_inv'),
            },
            {
                'display': 'Import Batches',
                'href': reverse('imb_inv'),
            },
            {
                'display': 'Staging Batches',
                'href': reverse('stb_inv'),
            },
            {
                'display': 'Tables',
                'href': reverse('tbl_inv'),
            },
            {
                'display': 'Admin Tools',
                'href': reverse('djhcup_staging|admin')
            }
        ]
        context['title'] = 'Hachoir: Staging'
        return context

ALLOWED_OBJ_DETAIL = [
    'DataSource',
    'File',
    'ImportBatch',
    'StagingBatch',
    'StagingTable',
    'Column'
]

class ObjectDetail(View):
    @method_decorator(login_required)
    def dispatch(self, request, obj_id, obj_type):
        if obj_type not in ALLOWED_OBJ_DETAIL:
            raise Exception("Invalid object type requested ({t})".format(t=obj_type))
        return globals()["ObjectDetail_%s" % (obj_type)].as_view()(request, obj_id=obj_id)

class ObjectDetail_DataSource(TemplateView):
    template_name = 'stg_detail_ds.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectDetail_DataSource, self).get_context_data(**kwargs)
        source = DataSource.objects.get(pk=self.kwargs['obj_id'])
        files = File.objects.filter(file_type__source=source)
        file_types = FileType.objects.filter(source=source)
        import_tables = StagingTable.objects.filter(imported_via__file__file_type__source=source)
        context.update({
            'title': str(source),
            'obj': source,
            'children': DataSource.objects.filter(parent=source),
            'files': {
                'content': files.exclude(file_type__content_type__in=['LOAD']),
                'load': files.filter(file_type__content_type__in=['LOAD']),
            },
            'file_types': file_types,
            'import_tables': import_tables,
        })
        return context

class ObjectDetail_File(TemplateView):
    template_name = 'stg_detail_f.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectDetail_File, self).get_context_data(**kwargs)
        f = File.objects.get(pk=self.kwargs['obj_id'])
        context.update({
            'title': 'File #{pk}'.format(pk=f.pk),
            'obj': f
        })
        return context

class ObjectDetail_ImportBatch(TemplateView):
    template_name = 'stg_detail_ibatch.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectDetail_ImportBatch, self).get_context_data(**kwargs)
        ibatch = ImportBatch.objects.get(pk=self.kwargs['obj_id'])
        enqueued = ibatch.importqueue_set.all()#.prefetch_related('file__get_absolute_url')
        context.update({
            'title': 'Details for %s' % ibatch,
            'obj': ibatch,
            'enqueued': enqueued,
            'eta': sum([f.est_runtime for f in enqueued])
        })
        return context

class ObjectDetail_StagingBatch(TemplateView):
    template_name = 'stg_detail_stbatch.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectDetail_StagingBatch, self).get_context_data(**kwargs)
        stbatch = StagingBatch.objects.get(pk=self.kwargs['obj_id'])
        enqueued = stbatch.stagingqueue_set.all()
        context.update({
            'title': 'Details for %s' % stbatch,
            'obj': stbatch,
            'enqueued': enqueued,
        })
        return context

class ObjectDetail_StagingTable(TemplateView):
    template_name = 'stg_detail_tbl.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectDetail_StagingTable, self).get_context_data(**kwargs)
        tbl = StagingTable.objects.get(pk=self.kwargs['obj_id'])
        context.update({
            'title': 'Details for %s' % tbl,
            'obj': tbl,
            'columns': tbl.column_set.all().order_by('name'),
        })
        return context

class ObjectDetail_Column(TemplateView):
    template_name = 'stg_detail_col.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectDetail_Column, self).get_context_data(**kwargs)
        col = Column.objects.get(pk=self.kwargs['obj_id'])
        context.update({
            'title': 'Details for %s' % col,
            'obj': col,
            'tbl': col.stg,
        })
        return context

class ObjectInventory(View):
    @method_decorator(login_required)
    def dispatch(self, request, obj_type, **kwargs):
        if obj_type not in ALLOWED_OBJ_DETAIL:
            raise Exception("Invalid object type requested ({t})".format(t=obj_type))
        return globals()["ObjectInventory_%s" % (obj_type)].as_view()(request, **kwargs)

class ObjectInventory_DataSource(TemplateView):
    template_name = 'stg_inv.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectInventory_DataSource, self).get_context_data(**kwargs)
        sources = DataSource.objects.all()
        sources_tl = sources.filter(parent__isnull=True)
        sources_lst = [o for o in sources_tl]
        context.update({
            'title': 'DataSource Inventory', 
            'counts': [
                {'name': 'Total DataSources specified in database', 'value': sources.count()},
                {'name': 'Top-level DataSources (without a parent DataSource)', 'value': sources_tl.count()},
            ],
            'objects': sources_lst
            })
        if len(sources_lst) == 0:
            # no sources found--offer to plug in the defaults
            context['links'].append({
                'display': 'Populate default source definitions for HCUP and Texas PUDF&rarr;',
                'href': reverse('source_populate_defaults'),
                })
        return context

class ObjectInventory_File(TemplateView):
    template_name = 'stg_inv_f.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectInventory_File, self).get_context_data(**kwargs)
        content = File.objects \
            .exclude(file_type__content_type='LOAD') \
            .order_by('state__abbreviation', 'year',
                      'file_type__source__abbreviation', 'file_type')
        loadfiles = File.objects \
            .filter(file_type__content_type='LOAD') \
            .order_by('state__abbreviation', 'year',
                      'file_type__source__abbreviation', 'file_type')
        context.update({
            'title': "File Inventory"
        })
        if ('state_abbr' in self.kwargs and
            self.kwargs['state_abbr'] != 'all'):
            st = self.kwargs['state_abbr']
            context['state_abbr'] = st
            content = content.filter(
                state__abbreviation=st)
            loadfiles = loadfiles.filter(
                state__abbreviation=st)
        else:
            context['state_abbr'] = 'all'
            
        
        if ('year' in self.kwargs and
            self.kwargs['year'] != 'all'):
            yr = self.kwargs['year']
            context['year'] = yr
            content = content.filter(
                year=yr)
            loadfiles = loadfiles.filter(
                year=yr)
        else:
            context['year'] = 'all'
        
        context['content'] = content
        context['loadfiles'] = loadfiles
        return context

class ObjectInventory_ImportBatch(TemplateView):
    template_name = 'stg_inv_ibatch.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectInventory_ImportBatch, self).get_context_data(**kwargs)
        imbs = ImportBatch.objects.all()
        started = imbs.filter(start__isnull=False, complete__isnull=True)
        not_started = imbs.filter(start__isnull=True)
        completed = imbs.filter(start__isnull=False, complete__isnull=False)
        context.update({
            'objects': imbs,
            'started': started,
            'not_started': not_started,
            'completed': completed,
            'title': "ImportBatch Inventory"
        })
        return context

class ObjectInventory_StagingBatch(TemplateView):
    template_name = 'stg_inv.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectInventory_StagingBatch, self).get_context_data(**kwargs)
        context.update({
            'objects': StagingBatch.objects.all(),
            'title': "StagingBatch Inventory"
        })
        return context

class ObjectInventory_StagingTable(TemplateView):
    template_name = 'stg_inv_tbl.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectInventory_StagingTable, self).get_context_data(**kwargs)
        stt = StagingTable.objects.all().order_by('category', '-name')
        context.update({
            'title': "StagingTable Inventory"
        })
        if ('state_abbr' in self.kwargs and
            self.kwargs['state_abbr'] != 'all'):
            st = self.kwargs['state_abbr']
            context['state_abbr'] = st
            stt = filter(lambda x: x.state == st, stt)
        else:
            context['state_abbr'] = 'all'
        
        if ('year' in self.kwargs and
            self.kwargs['year'] != 'all'):
            yr = self.kwargs['year']
            context['year'] = yr
            stt = filter(lambda x: x.year == int(yr), stt)
        else:
            context['year'] = 'all'
        
        stt_yr_sorted = sorted(
            stt,
            lambda x, y: cmp(x.year, y.year)
        )
        
        stt_styr_sorted = sorted(
            stt_yr_sorted,
            lambda x, y: cmp(x.state.lower(), y.state.lower())
        )
        
        context['objects'] = stt_styr_sorted
        return context


class DiscoverFiles(View):

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(DiscoverFiles, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        tasks.discover_files.delay()
        messages.info(request, 'File discovery task has been dispatched. You will receive an email once the process is complete.')
        return redirect('file_inv')

class MatchFiles(View):

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(MatchFiles, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        tasks.match_files.delay()
        messages.info(request, 'File matching task has been dispatched. You will receive an email once the process is complete.')
        return redirect('file_inv')

class CreateUnimportedBatch(View):

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(CreateUnimportedBatch, self).dispatch(*args, **kwargs)

    def post(self, request):
        tasks.create_unimported_batch.delay()
        messages.info(request, 'A task to create a batch of unimported files has been dispatched. You will receive an email once the process is complete.')
        return redirect('imb_inv')


class CreateUnprocessedBatch(View):

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(CreateUnprocessedBatch, self).dispatch(*args, **kwargs)

    def post(self, request):
        tasks.create_unprocessed_batch.delay()
        messages.info(request, 'A task to create a batch of unprocessed files has been dispatched. You will receive an email once the process is complete.')
        return redirect('stb_inv')


class RunBatch(View):

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(RunBatch, self).dispatch(*args, **kwargs)

    def post(self, request, obj_id, obj_type):
    
        ALLOWED_BATCH_TYPES = [
            'ImportBatch',
            'StagingBatch',
        ]

        if obj_type == 'ImportBatch':
            logger.info('Attempting to call a Celery task for ImportBatch %i' % (int(obj_id)))
            tresult = tasks.batch_import.delay(obj_id)
            response = "ImportBatch has been dispatched to Celery in thread %s." % (tresult)
            logger.info(response)
            return ObjectDetail.as_view()(request, obj_id, obj_type)
        
        elif obj_type == 'StagingBatch':
            logger.info('Attempting to call a Celery task for StagingBatch %i' % (int(obj_id)))
            tresult = tasks.batch_stage.delay(obj_id)
            response = "StagingBatch has been dispatched to Celery in thread %s." % (tresult)
            logger.info(response)
            return ObjectDetail.as_view()(request, obj_id, obj_type)

        else:
            raise Exception("Requested batch type {t} not in allowed types: {a}"\
                .format(t=obj_type, a=ALLOWED_BATCH_TYPES))


class ResetDeadBatches(View):
    """Dispatches a celery task to reset interrupted ImportBatch objects and their associated ImportQueue objects.
    """

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(ResetDeadBatches, self).dispatch(*args, **kwargs)

    def post(self, request):
        logger.info('Attempting to call a Celery task for resetting dead batches')
        tasks.reset_dead.delay()
        messages.info(request, 'A task to reset dead batches has been dispatched. You will receive an email once the process is complete.')
        return redirect('djhcup_staging|admin')

class Admin(TemplateView):
    template_name = 'stg_admin.html'

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(Admin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Admin, self).get_context_data(**kwargs)
        context['title'] = 'Staging Admin Tools'
        return context
