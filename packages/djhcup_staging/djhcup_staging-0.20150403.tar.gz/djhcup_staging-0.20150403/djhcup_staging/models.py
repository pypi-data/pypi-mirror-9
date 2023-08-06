# builtins
import os
import datetime
import logging


# third party modules
import pyhcup


# django modules
from django.utils.timezone import utc
from django.db import models
from django.db.models import Q
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.conf import settings


# local project modules
from djhcup_core.utils import get_pgcnxn
from djhcup_core.defaults import DATETIME_FORMAT


# set some constants
ALLOWED_LOG_LEVELS = ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


# start a logger
default_logger = logging.getLogger('default')


# Create your models here.
class State(models.Model):
    abbreviation = models.CharField(max_length=2, blank=False,
                                    db_index=True, help_text='Two-letter abbreviation for state')
    name = models.CharField(max_length=200, blank=False,
                            help_text='Full name of state')
    def __unicode__(self):
        return 'State: %s (%s)' % (self.name, self.abbreviation)


class DataSource(models.Model):
    """This is a node-based taxonomy of data sources. E.g. HCUP SID CORE is a data source abbreviated CORE, with parent SID, with parent HCUP"""
    parent = models.ForeignKey('self', default=None, blank=True, null=True)
    abbreviation = models.CharField(max_length=20, blank=False,
                                    db_index=True, help_text='Abbreviated name of data source e.g. SID')
    name = models.CharField(max_length=200, blank=False,
                            help_text='Full name of data source e.g. State Inpatient Database')
    description = models.TextField(blank=True)
        
    def _descriptor(self, separator="_"):
        abbrs = [self.abbreviation]
        if self.parent:
            current = self
            while current.parent:
                current = current.parent
                abbrs.append(current.abbreviation)
        return separator.join(abbrs[::-1])#reverse the order so it proceeds heirarchically
        
    def _hr_descriptor(self):
        return '%s' % self._descriptor(separator=">>")
    hr_descriptor = property(_hr_descriptor)
    
    def _mr_descriptor(self):
        return self._descriptor()
    mr_descriptor = property(_mr_descriptor)
    
    def _top_level_source(self):
        source = self
        while source.parent is not None:
            source = source.parent
        return source
    top_level_source = property(_top_level_source)
    
    def get_absolute_url(self):
        return reverse(
            'ds_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'DataSource'}
        )
    
    def __unicode__(self):
        return "<DataSource: {hr}>".format(hr=self.hr_descriptor)


class FileType(models.Model):
    """Holds regular expression patterns associated with filenames for DataSources

    Also indicates whether the pattern indicates a loadfile vs content file and if the file is compressed.
    """
    source = models.ForeignKey('DataSource')
    pattern = models.TextField(blank=False, help_text=escape('Regular expression for matching filenames. Must capture groups <state_abbr>, <year>, and <file_extension>, which will be used when recording a DataFile object later. For example, an HCUP SEDD CORE data file pattern might look like (?P<state_abbr>[A-Z]{2})_SEDD_(?P<year>[0-9]{4})_CORE\\.(?P<file_extension>asc)'))
    TYPE_CHOICES = [('LOAD', 'Loadfile (defines content)'),
                    ('CONTENTNH', 'Content (actual data) without header row'),
                    ('CONTENTWH', 'Content (actual data) with header row'),
                    ]
    content_type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=False, default='CONTENTNH')
    COMPRESSION_CHOICES = [('NONE', 'Uncompressed'),
                      ('ZIP', 'ZIP format (PKZIP)'),
                      ]
    compression = models.CharField(max_length=10, choices=COMPRESSION_CHOICES, blank=False, default='NONE')
    
    def _hr_descriptor(self):
        """Returns a shorthand description of the file type and compression"""
        if self.compression == 'NONE':
            compression_desc = 'uncompressed'
        else:
            compression_desc = '%scompressed' % (self.compression.lower())
        return '%s_%s' % (self.content_type.lower(), compression_desc)
    hr_descriptor = property(_hr_descriptor)
    
    def __unicode__(self):
        return '<FileType: %s %s>' % (self.hr_descriptor, self.source)


class File(models.Model):
    file_type = models.ForeignKey('FileType')
    state = models.ForeignKey('State')
    year = models.IntegerField(blank=False, null=False, db_index=True)
    quarter = models.IntegerField(blank=True, null=True, default=None)
    filename = models.CharField(max_length=50, blank=False)
    full_path = models.CharField(max_length=200, blank=False)
    size_on_disk = models.BigIntegerField(blank=True, null=True)
    
    #partner file for actual loading, if this is a content file
    loadfile = models.ForeignKey('self', blank=True, default=None, null=True)
    
    
    def _hr_size(self, XiB=True):
        """Returns size in XiB or XB with appropriate abbreviation, usually MiB"""
        if self.size_on_disk:
            if XiB:
                unit_base = 'iB'
                size = float(self.size_on_disk)/1048576
            else:
                unit_base = 'B'
                size = float(self.size_on_disk)/1000000
            
            if size >= 1.0:
                return "{size}M{unit_base}".format(size=format(size, '.1f'),
                                                    unit_base=unit_base)
            elif size >= 0.001:
                return "{size}K{unit_base}".format(size=format(size*1000, '.1f'),
                                                    unit_base=unit_base)
            else:
                return "Less than 1K{unit_base}".format(unit_base=unit_base)
            
        else:
            return 'file size unknown'
    hr_size = property(_hr_size)
    
    
    def _est_rows(self):
        if self.file_type.compression == 'NONE':
            full_size = self.size_on_disk/1048576
        else:
            full_size = 5*self.hr_size/1048576
        return 9850*full_size
    est_rows = property(_est_rows)
    
    
    def open(self):
        c = self.file_type.compression
        
        if c == 'NONE':
            # uncompressed
            handle = pyhcup.parser._open(self.full_path,
                                         self.state.abbreviation,
                                         self.year,
                                         self.file_type.source.abbreviation,
                                         database=self.file_type.source.parent.abbreviation
                                         )
        elif c == 'ZIP':
            # pkzip compression
            handle = pyhcup.hachoir.openz(os.path.dirname(self.full_path), self.filename)
        else:
            raise Exception("Unknown compression type %s; unable to generate file handle." % c)
        
        return handle
    
    class Meta:
        verbose_name = 'file'
        verbose_name_plural = 'files'
        ordering = ['file_type__source', 'state__abbreviation', 'year', 'file_type__compression', 'filename']
    
    def get_absolute_url(self):
        return reverse(
            'file_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'File'}
        )
    
    def __unicode__(self):
        return '<File #%s: %s (%s)>' % (self.pk, self.filename, self.file_type)


class ImportBatch(models.Model):
    name = models.CharField(max_length=200, blank=True, help_text="Optional name for this batch of imports")
    description = models.TextField(blank=True, help_text="Optional description for this batch of imports")
    STATUS_CHOICES = [('NEW', 'Not started'),
                      ('QUEUED', 'Request for processing sent'),
                      ('DISPATCHED', 'Sent to Celery'),
                      ('RECEIVED', 'Received by Celery'),
                      ('IN PROCESS', 'Running'),
                      ('FAILED', 'Failed to complete'),
                      ('SUCCESS', 'Completed successfully'),
                      ]
    status = models.CharField(max_length=15, blank=False, null=True, default='NEW', choices=STATUS_CHOICES)
    celery_task_id = models.TextField(blank=True, null=True, default=None)
    
    start = models.DateTimeField(blank=True, null=True, default=None)
    complete = models.DateTimeField(blank=True, null=True, default=None)

    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    class Meta:
        verbose_name_plural = 'import batches'
        
    def _hr_start(self):
        return self.start.strftime(DATETIME_FORMAT)
    hr_start = property(_hr_start)
    
    def _hr_complete(self):
        return self.complete.strftime(DATETIME_FORMAT)
    hr_complete = property(_hr_complete)
    
    def _runtime(self):
        if self.start and self.complete:
            return self.complete - self.start
        else:
            return None
    runtime = property(_runtime)
    
    def _hr_runtime(self):
        """Batch runtime in hours"""
        if self.runtime is not None:
            td = self.runtime
            return td.days*24+td.seconds/float(3600)
        else:
            return None
    hr_runtime = property(_hr_runtime)
    
    
    def fail(self):
        self.status = 'FAILED'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def success(self):
        self.status = 'SUCCESS'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def successful(self):
        if self.status == 'SUCCESS':
            return True
        else:
            return False
    
    def log(self, message, level='INFO', status=None, logger=None):
        """Emit a log message at the specified log level and optionally update the ImportQueue object status attribute.
        """
        
        if level not in ALLOWED_LOG_LEVELS:
            raise Exception("ImportBatch %s] Invalid log level specified: %s" % (self.pk, level))
        else:
            level = getattr(logging, level)
        
        if logger is None:
            logger = default_logger
        
        if status is not None:
            self.status = status
        
        self.save()
        
        logger_message = "[ImportBatch %s] %s" % (self.pk, message)
        logger.log(level, logger_message)
        return True
    
    
    def get_absolute_url(self):
        return reverse(
            'imb_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'ImportBatch'}
        )
    
    def __unicode__(self):
        c_items = ImportQueue.objects.filter(batch=self).count()
        return "ImportBatch %i [%s]: %d files" % (self.pk, self.status, c_items)


class ImportQueue(models.Model):
    batch = models.ForeignKey('ImportBatch')
    file = models.ForeignKey('File',
        limit_choices_to = Q(loadfile__isnull=False, file_type__content_type='CONTENTNH') | Q(file_type__content_type='CONTENTWH'),
        help_text="Must point to a non-loadfile with a loadfile matched to it; this file and the import batch's destination must belong to the same data source or the batch will fail to execute")
    start = models.DateTimeField(blank=True, null=True, default=None)
    complete = models.DateTimeField(blank=True, null=True, default=None)
    STATUS_CHOICES = [('NEW', 'Not started'),
                      ('QUEUED', 'Request for processing sent'),
                      ('DISPATCHED', 'Sent to Celery'),
                      ('RECEIVED', 'Received by Celery'),
                      ('IN PROCESS', 'Running'),
                      ('FAILED', 'Failed to complete'),
                      ('SUCCESS', 'Completed successfully'),
                      ]
    status = models.CharField(max_length=15, blank=False, null=True, default='NEW', choices=STATUS_CHOICES)
    message = models.TextField(blank=True, null=True, default=None)
    message_at = models.DateTimeField(blank=True, null=True, default=None)
    celery_task_id = models.TextField(blank=True, null=True, default=None)
    
    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    
    def _hr_start(self):
        return self.start.strftime(DATETIME_FORMAT)
    hr_start = property(_hr_start)
    
    
    def _hr_complete(self):
        return self.complete.strftime(DATETIME_FORMAT)
    hr_complete = property(_hr_complete)
    
    
    def _runtime(self):
        if self.start and self.complete:
            return self.complete - self.start
        else:
            return None
    runtime = property(_runtime)
    
    
    def _hr_runtime(self):
        """File runtime in hours"""
        if self.runtime is not None:
            td = self.runtime
            return td.days*24+td.seconds/float(3600)
        else:
            return None
    hr_runtime = property(_hr_runtime)
    
    
    def _est_runtime(self):
        # default to average across all SID CORE state-years as of 2014-03-28
        width = 164
        try:
            # attempt to find precise width for this file
            m = pyhcup.meta.get(self.file.state.abbreviation, self.file.year)
            if m is not None:
                width = len(m)
        except:
            pass
        
        est_values_per_minute = 4.5 * 10**6
        rows_per_minute = est_values_per_minute / float(width)
        rows_per_hour = rows_per_minute * 60
        
        return self.file.est_rows/(rows_per_hour)
    est_runtime = property(_est_runtime)
    
    
    class Meta:
        verbose_name = 'enqueued import'
        verbose_name_plural = 'enqueued imports'
    
    
    def log(self, message, level='INFO', status=None, logger=None):
        """Emit a log message at the specified log level and optionally update the ImportQueue object status attribute.
        """
        
        if level not in ALLOWED_LOG_LEVELS:
            raise Exception("Invalid log level specified: %s" % level)
        else:
            level = getattr(logging, level)
        
        if logger is None:
            logger = default_logger
        
        if status is not None:
            self.status = status
        
        self.message = message
        self.save()
        
        logger_message = "[ImportQueue item %s] %s" % (self.pk, message)
        logger.log(level, logger_message)
        return True
    
    
    def fail(self, message=None, logger=None, level='ERROR'):
        self.status = 'FAILED'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        
        if message is not None:
            self.log(message, level=level, logger=logger)
        return True
    
    
    def success(self, message=None, logger=None):
        self.status = 'SUCCESS'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        
        if message is not None:
            self.log(message, logger=logger)
        
        return True
    
    
    def successful(self):
        if self.status == 'SUCCESS':
            return True
        else:
            return False
    
    
    def record_columns(self):
        tls = self.file.file_type.source.top_level_source.abbreviation
        cols_saved = 0
        
        if tls == 'HCUP':
            meta = pyhcup.sas.meta_from_sas(self.file.loadfile.full_path)
            augmented = pyhcup.meta.augment(meta)
            
            # store the columns for future reference
            for k, v in augmented.T.to_dict().iteritems():
                #col_supplemental_meta = pyhcup.db.col_from_invalue(v['informat'])
                col = Column(
                    iq=self,
                    name=v['field'],
                    col_type=v['data_type'].upper(),
                    col_scale=v['scale'],
                    col_precision=v['length'],
                    informat=v['informat'],
                    )
                col.save()
                cols_saved += 1
        
        elif tls == 'PUDF':
            meta = pyhcup.tx.meta_from_txt(self.file.loadfile.full_path)
            augmented = pyhcup.meta.augment(meta, dialect='PUDF')
            
            # store the columns for future reference
            for k, v in augmented.T.to_dict().iteritems():
                # col_supplemental_meta = pyhcup.db.col_from_invalue(v['informat'])
                col = Column(
                    iq=self,
                    name=v['field'],
                    col_type=v['data_type'].upper(),
                    col_scale=v['scale'],
                    col_precision=v['length'],
                    # informat=v['informat'],
                    )
                col.save()
                cols_saved += 1
        else:
            raise Exception('No loadfile parser associated with top-level source %s' % tls)
        
        return cols_saved
    
    
    def get_meta(self):
        tls = self.file.file_type.source.top_level_source.abbreviation
        
        if tls == 'HCUP':
            loader = pyhcup.sas.meta_from_sas
        
        elif tls == 'PUDF':
            loader = pyhcup.tx.meta_from_txt
        
        else:
            raise Exception('No loadfile parser associated with top-level source %s' % tls)
        
        loadfile = self.file.loadfile
        
        if loadfile is None:
            raise Exception('No loadfile associated with file %s'% self.file)
        else:
            meta = loader(loadfile.full_path)
        
        return meta
    
    def __unicode__(self):
        return "ImportQueue item %s [%s]: %s" % (self.pk, self.status, self.file.filename)
    

class StagingBatch(models.Model):
    #destination = models.ForeignKey('ImportTable')
    name = models.CharField(max_length=200, blank=True, help_text="Optional name for this batch of staging work")
    description = models.TextField(blank=True, help_text="Optional description for this batch of staging work")
    STATUS_CHOICES = [('NEW', 'Not started'),
                      ('QUEUED', 'Request for processing sent'),
                      ('DISPATCHED', 'Sent to Celery'),
                      ('RECEIVED', 'Received by Celery'),
                      ('IN PROCESS', 'Running'),
                      ('FAILED', 'Failed to complete'),
                      ('SUCCESS', 'Completed successfully'),
                      ]
    status = models.CharField(max_length=15, blank=False, null=True, default='NEW', choices=STATUS_CHOICES)
    celery_task_id = models.TextField(blank=True, null=True, default=None)
    
    start = models.DateTimeField(blank=True, null=True, default=None)
    complete = models.DateTimeField(blank=True, null=True, default=None)

    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    class Meta:
        verbose_name_plural = 'staging batches'
        
    def _hr_start(self):
        return self.start.strftime(DATETIME_FORMAT)
    hr_start = property(_hr_start)
    
    def _hr_complete(self):
        return self.complete.strftime(DATETIME_FORMAT)
    hr_complete = property(_hr_complete)
    
    def _runtime(self):
        if self.start and self.complete:
            return self.complete - self.start
        else:
            return None
    runtime = property(_runtime)
    
    def _hr_runtime(self):
        """Batch runtime in hours"""
        if self.runtime is not None:
            td = self.runtime
            return td.days*24+td.seconds/float(3600)
        else:
            return None
    hr_runtime = property(_hr_runtime)
    
    
    def fail(self):
        self.status = 'FAILED'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def success(self):
        self.status = 'SUCCESS'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def successful(self):
        if self.status == 'SUCCESS':
            return True
        else:
            return False
    
    
    def log(self, message, level='INFO', status=None, logger=None):
        """Emit a log message at the specified log level and optionally update the ImportQueue object status attribute.
        """
        
        if level not in ALLOWED_LOG_LEVELS:
            raise Exception("StagingBatch %s] Invalid log level specified: %s" % (self.pk, level))
        else:
            level = getattr(logging, level)
        
        if logger is None:
            logger = default_logger
        
        if status is not None:
            self.status = status
        
        self.message = message
        self.save()
        
        logger_message = "[StagingBatch %s] %s" % (self.pk, message)
        logger.log(level, logger_message)
        return True
    
    def get_absolute_url(self):
        return reverse(
            'stb_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'StagingBatch'}
        )
    
    def __unicode__(self):
        c_items = StagingQueue.objects.filter(batch=self).count()
        return "StagingBatch %i [%s]: %d files" % (self.pk, self.status, c_items)


class StagingQueue(models.Model):
    batch = models.ForeignKey('StagingBatch')
    input_ht = '''
        In the case of staging operations with a single input, set
        this attribute equal to it. For staging operations with
        multiple inputs, this is typically a reference to a CORE_SOURCE table,
        but may also be a CHARGES_SOURCE table in some instances.
        '''
    stg_input = models.ForeignKey('StagingTable', related_name='stg_input',
                                  help_text=input_ht)
    charges_input = models.ForeignKey('StagingTable', related_name='charges_input',
                                      help_text='CHARGES, if required (*never* CHARGES_SOURCE).',
                                      null=True, default=None, blank=True)
    pr_input = models.ForeignKey('StagingTable', related_name='pr_input',
                                 help_text='PR, if required.',
                                 null=True, default=None, blank=True)
    uflag_input = models.ForeignKey('StagingTable', related_name='uflag_input',
                                    help_text='UFLAGS, if required.',
                                    null=True, default=None, blank=True)
    dte_input = models.ForeignKey('StagingTable', related_name='dte_input',
                                  help_text='DTE_SOURCE, if required.',
                                  null=True, default=None, blank=True)
    aha_input = models.ForeignKey('StagingTable', related_name='aha_input',
                                  help_text='AHALINK_SOURCE, if required.',
                                  null=True, default=None, blank=True)
    severity_input = models.ForeignKey('StagingTable', related_name='severity_input',
                                  help_text='SEVERITY_SOURCE, if required.',
                                  null=True, default=None, blank=True)
    dx_pr_grps_input = models.ForeignKey('StagingTable', related_name='dx_pr_grps_input',
                                  help_text='DX_PR_GRPS_SOURCE, if required.',
                                  null=True, default=None, blank=True)
    
    
    # Anyone looking at this code must, by now, wonder why more of
    # this wasn't made in a modular fashion. For example, why not
    # have categories of table types be held in their own table,
    # so that new categories can be introduced and logic for
    # managing their transformations could be generated
    # dynamically?
    #
    # The answer is: that's total overkill. We have fewer than
    # ten distinct transformations, even if you include the
    # initial loading (which I don't, as it is semantically quite
    # different). And some kind of generalizable code for column
    # A becomes column B with transformation C in between is way
    # more trouble than it is worth.
    #
    # Similarly, making all the "Queue" style objects into a
    # single model, where some are file imports off a disk and
    # others are transformations of data in staging tables, is
    # perhaps the height of idealism but unquestionably the utter
    # dregs of pedantry. At this scale, it is an incredibly
    # inefficient approach. And, at a tremendously increased
    # scale, the overhead of a second table due to dividing work
    # into within-database and into-database is dwarfed by the
    # weight of everything else.
    #
    # Another question surely brought to mind by now: why this
    # missive?
    #
    # The answer is: in case I start thinking consolidating these
    # might be a good idea.
    
    CAT_CHOICES = [
        #('CORE_SOURCE','CORE data in wide format, from source (no derived/updated cols)'),
        #('CHARGES_SOURCE','Charges data, from source (no wide-to-long conversion)'),
        #('DAYSTOEVENT_SOURCE','DaysToEvent and VisitLink data, from source (straight csv load)'),
        #('AHALINK_SOURCE','American Hospital Association link data, from source (straight csv load)'),
        ('CHARGES','Charges data in long format (converted from wide source if necessary)'),
        ('DX','Diagnoses data in long format (from CORE_SOURCE)'),
        ('PR','Procedures data in long format (from CORE_SOURCE)'),
        ('UFLAGS','Utilization flag data, long format (from CORE_SOURCE, CHARGES, and PR)'),
        ('CORE_PROCESSED','CORE Processed: CORE, DaysToEvent/VisitLink, wide charges, wide uflags'),
    ]
    category = models.CharField(max_length=100, choices=CAT_CHOICES, blank=False, help_text="Category of data to build from stg_input and insert into stg_output")
    
    stg_output = models.ForeignKey('StagingTable', related_name='stg_output', default=None, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True, default=None)
    complete = models.DateTimeField(blank=True, null=True, default=None)
    STATUS_CHOICES = [('NEW', 'Not started'),
                      ('QUEUED', 'Request for processing sent'),
                      ('DISPATCHED', 'Sent to Celery'),
                      ('RECEIVED', 'Received by Celery'),
                      ('IN PROCESS', 'Running'),
                      ('FAILED', 'Failed to complete'),
                      ('SUCCESS', 'Completed successfully'),
                      ]
    status = models.CharField(max_length=15, blank=False, null=True, default='NEW', choices=STATUS_CHOICES)
    message = models.TextField(blank=True, null=True, default=None)
    message_at = models.DateTimeField(blank=True, null=True, default=None)
    celery_task_id = models.TextField(blank=True, null=True, default=None)
    
    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    def _hr_start(self):
        return self.start.strftime(DATETIME_FORMAT)
    hr_start = property(_hr_start)
    
    def _hr_complete(self):
        return self.complete.strftime(DATETIME_FORMAT)
    hr_complete = property(_hr_complete)
    
    def _runtime(self):
        if self.start and self.complete:
            return self.complete - self.start
        else:
            return None
    runtime = property(_runtime)
    
    def _hr_runtime(self):
        """File runtime in hours"""
        if self.runtime is not None:
            td = self.runtime
            return td.days*24+td.seconds/float(3600)
        else:
            return None
    hr_runtime = property(_hr_runtime)
    
    class Meta:
        verbose_name = 'enqueued staging'
        verbose_name_plural = 'enqueued stagings'
    
    def log(self, message, level='INFO', status=None, logger=None):
        """Emit a log message at the specified log level and optionally update the ImportQueue object status attribute.
        """
        
        if level not in ALLOWED_LOG_LEVELS:
            raise Exception("Invalid log level specified: %s" % level)
        else:
            level = getattr(logging, level)
        
        if logger is None:
            logger = default_logger
        
        if status is not None:
            self.status = status
        
        self.message = message
        self.save()
        
        logger_message = "[StagingQueue item %s] %s" % (self.pk, message)
        
        logger.log(level, logger_message)
        return True
    
    def fail(self, message=None, logger=None, level='ERROR'):
        self.status = 'FAILED'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        
        if message is not None:
            self.log(message, level=level, logger=logger)
        
        return True
    
    def success(self, message=None, logger=None):
        self.status = 'SUCCESS'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        
        if message is not None:
            self.log(message, logger=logger)
        
        return True
    
    def successful(self):
        if self.status == 'SUCCESS':
            return True
        else:
            return False
    
    def __unicode__(self):
        return "StagingQueue item %s [%s]" % (self.pk, self.status)
    

class StagingTable(models.Model):
    """This is a record of staging tables created/populated
    """
    #source = models.ForeignKey('DataSource', help_text="Data source for which this table was created as a 'master' import table")
    imported_via = models.ForeignKey('ImportQueue', blank=True, default=None, null=True)
    parent = models.ForeignKey('self', default=None, blank=True, null=True)
    name = models.CharField(max_length=250, blank=False)
    description = models.TextField(default=None, blank=True, null=True)
    schema = models.CharField(max_length=250, blank=True)
    database = models.CharField(max_length=250, blank=True, help_text="Leave blank to use default connection specified in Django's setings.py file")
    
    STG_CAT_CHOICES = [
        ('CORE_SOURCE','CORE data in wide format, from source (no derived/updated cols)'),
        ('CHARGES_SOURCE','Charges data, from source (no wide-to-long conversion)'),
        ('DAYSTOEVENT_SOURCE','DaysToEvent and VisitLink data, from source (straight csv load)'),
        ('AHALINK_SOURCE','American Hospital Association link data, from source'),
        ('SEVERITY_SOURCE','AHRQ comorbidity measures, from source'),
        ('DX_PR_GRPS_SOURCE','DX_PR_GRPS, from source'),
        ('CHARGES','Charges data in long format (converted from wide source if necessary)'),
        ('DX','Diagnoses data in long format (from CORE_SOURCE)'),
        ('PR','Procedures data in long format (from CORE_SOURCE)'),
        ('UFLAGS','Utilization flag data, long format (from CORE_SOURCE, CHARGES, and PR)'),
        ('CORE_PROCESSED','CORE Processed: CORE, DaysToEvent/VisitLink, wide charges, wide uflags'),
        ('SUPPLEMENTARY', 'Supplementary data table - join fields required')
    ]
    category = models.CharField(max_length=100, choices=STG_CAT_CHOICES, blank=False)
    wip = models.BooleanField(default=True, help_text="This StagingTable is work-in-progress, and should not be used.")
    records = models.IntegerField()
    
    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    # methods/properties for determining state and year
    def _state_abbr(self):
        if self.parent is None:
            if self.imported_via is not None:
                return self.imported_via.file.state.abbreviation
            else:
                return None
        else:
            return self.parent.state
    state = property(_state_abbr)
        
    def _year(self):
        if self.parent is None:
            if self.imported_via is not None:
                return self.imported_via.file.year
            else:
                return None
        else:
            return self.parent.year
    year = property(_year)
    
    def _data_source(self):
        if self.parent is None:
            if self.imported_via is not None:
                return self.imported_via.file.file_type.source
            else:
                return None
        else:
            return self.parent.data_source
    data_source = property(_data_source)
    
    def _col_count(self):
        return self.column_set.count()
    col_count = property(_col_count)
    
    def __unicode__(self):
        return "StagingTable %d: %s" % (self.pk, self.name)
    
    # overwrite method to drop table as well by default
    def delete(self, drop_table=True, *args, **kwargs):
        if drop_table:
            cnxn = get_pgcnxn()
            drop_result = pyhcup.db.pg_drop(cnxn, self.name)
            if drop_result == True:
                default_logger.info('Dropped table {table} from database'.format(table=self.name))
            else:
                default_logger.error('Unable to drop table {table} from database'.format(table=self.name))
        
        super(StagingTable, self).delete(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse(
            'tbl_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'StagingTable'}
        )

class StagingDefinition(models.Model):
    table = models.ForeignKey('StagingTable', related_name='+')
    join_to = models.ForeignKey('StagingTable', related_name='+')
    join_on = models.ManyToManyField('JoinDefinition')
    columns = models.ManyToManyField('Column')  # TODO: add validation to make sure cols all belong to table

class JoinDefinition(models.Model):
    join_left = models.ForeignKey('Column', related_name='+')
    join_right = models.ForeignKey('Column', related_name='+')
    op = models.CharField(max_length=4, default='=')  # Table 9-1 http://www.postgresql.org/docs/9.3/static/functions-comparison.html

class Column(models.Model):
    """Records details on a given column most typically after that column has been imported.
    
    Required attributes: name, count_notnull, count_null
    
    Optional attributes: description, min, max, stddev_samp, stddev_pop, mean
    """
    stg = models.ForeignKey('StagingTable', null=True)
    name = models.CharField(max_length=200, blank=False, db_index=True)
    description = models.TextField(blank=True, null=True,
                                   help_text='The description provided by HCUP')
    TYPE_CHOICES = [
        ('VARCHAR', 'Character (string)'),
        ('NUMERIC', 'Numeric (decimal)'),
        ('INT', 'Integer (+/- 2.1E8)'),
        ('BIGINT', 'Integer (+/- 9.2E18)'),
        ('BOOLEAN', 'True/False'),
    ]
    col_type = models.CharField(max_length=100, choices=TYPE_CHOICES, blank=False)
    col_scale = models.IntegerField(blank=True, null=True, help_text='Decimal places for numeric fields')
    col_precision = models.IntegerField(blank=True, null=True, help_text='Total sigfigs for numeric fields')
    informat = models.CharField(max_length=100, blank=True, default=None, null=True,
                                help_text='SAS load informat this column is based on, if applicable')
    STATUS_CHOICES = [
        ('NONE', 'Validation has not been attempted'),
        ('UNAVAILABLE_AUTO', 'HCUP summary stats automatically detected as unavailable'),
        ('UNAVAILABLE_MANUAL', 'HCUP summary stats manually detected as unavailable'),
        ('VALID_AUTO', 'Validated automatically by comparison with HCUP summary stats'),
        ('VALID_MANUAL', 'Validated manually'),
        ('VALID_OVERRIDE', 'Marked as valid, overriding a known discrepancy with HCUP summary stats'),
        ('FAILED_AUTO', 'Failed validation automatically by comparison with HCUP summary stats'),
        ('FAILED_MANUAL', 'Failed validation manually by comparison with HCUP summary stats'),
        ('FAILED_OVERRIDE', 'Marked as failed, overriding an automatic validation'),
    ]
    integrity_status = models.CharField(max_length=100, choices=STATUS_CHOICES, blank=False, default='NONE')
    integrity_detail = models.TextField(blank=True, null=True)
    count_notnull = models.IntegerField(help_text='Count of non-null values.')
    count_null = models.IntegerField(help_text='Count of null values.')
    min = models.DecimalField(max_digits=50, decimal_places=6,
                              blank=True, default=None, null=True)
    max = models.DecimalField(max_digits=50, decimal_places=6,
                              blank=True, default=None, null=True)
    stddev_pop = models.DecimalField(max_digits=50, decimal_places=6,
                                     blank=True, default=None, null=True)
    stddev_samp = models.DecimalField(max_digits=50, decimal_places=6,
                                      blank=True, default=None, null=True)
    mean = models.DecimalField(max_digits=50, decimal_places=6,
                               blank=True, default=None, null=True)
    ref_col = models.ForeignKey('ReferenceColumn', blank=True, default=None,
                                null=True)
    
    def __unicode__(self):
        return "<Column %s: %s.%s (%s non-null values)>" % (self.pk, self.stg.name, self.name, self.count_notnull)
    
    def match_ref_col(self, logger=None):
        if logger is None:
            logger = default_logger
        
        if self.ref_col == None:
            # 
            f = self.stg.imported_via.file
            ds = f.file_type.source
            st = f.state
            yr = f.year
            name = self.name
            qs = ReferenceColumn.objects.filter(source=ds, state=st,
                                                year=yr, name__iexact=name)
            if len(qs) == 1:
                self.ref_col = qs[0]
                self.save()
                logger.info("Successfully matched Column %s with ReferenceColumn %s" % (self.pk, self.ref_col.pk))
                return True
            elif len(qs) > 1:
                logger.warning("Found %s ReferenceColumn entries matching Column %s (%s); Column.integrity_status will be updated to UNAVAILABLE_AUTO. The entries were: %s." % (len(qs), self.pk, self.name, qs))
                self.integrity_status = 'UNAVAILABLE_AUTO'
                self.save()
                return False
            else:
                logger.info("Found no ReferenceColumn entry matching Column %s (%s); Column.integrity_status will be updated to UNAVAILABLE_AUTO." % (self.pk, self.name))
                self.integrity_status = 'UNAVAILABLE_AUTO'
                self.save()
                return False
        else:
            logger.warning("match_ref_col() called on Column %s with ref_col already set to ReferenceColumn %s. match_ref_col() will not proceed." % (self.pk, self.ref_col.pk))
            return None
    
    def validate(self, tolerance=0.01):
        """
        Attempts to validate the integrity of data in this Column by
        comparing summary stats with those in ReferenceColumn ref_col.
        
        Returns None if ref_col cannot be found, False if the
        validation fails (observed values are outside of reference by
        more than tolerance, where tolerance is a percentage), or True.
        
        Updates self.integrity_status based on results.
        """
        if self.ref_col == None:
            # will attempt to match a reference column and re-do the
            # validation.
            match_attempt = self.match_ref_col()
            if match_attempt == True:
                return self.validate(tolerance=tolerance)
            else:
                return None
        else:
            all_summstat_attr = [
                'count_notnull',
                'count_null',
                'min',
                'max',
                'stddev_samp', # HCUP uses this in their summary stats
                'mean',
            ]
            
            # comps are attribute names for comparison.
            # we exclude any where Column.attr is None
            comps = [i for i in all_summstat_attr
                     if getattr(self, i) is not None]
            
            ref = self.ref_col
            issues = []
            results = []
            for attr in comps:
                # look through all the comparison attr
                # and build a list based on comparisons:
                # None for ref_col.attr == None
                # True for self.attr between ref_col.attr*(1 plus-minus tolerance)
                # else False
                ref_val = getattr(ref, attr)
                
                if ref_val == None:
                    results.append(None)
                    issues.append("No reference value for %s" % attr)
                else:
                    obs_val = getattr(self, attr)
                    ceiling = (1+tolerance)*ref_val
                    floor = (1-tolerance)*ref_val
                    if obs_val >= floor and obs_val <= ceiling:
                        results.append(True)
                    else:
                        issue = "Observed value {obs_val} outside reference value {ref_val} * (1 plus-minus {tolerance})". \
                            format(obs_val=obs_val, ref_val=ref_val, tolerance=tolerance)
                        issues.append(issue)
                        results.append(False)
                
                if self.integrity_detail == None:
                    self.integrity_detail = '\n'.join(issues)
                else:
                    self.integrity_detail += '\n'.join(issues)
                
                if False in results:
                    self.integrity_status = 'FAILED_AUTO'
                    self.save()
                    return False
                elif True in results:
                    self.integrity_status = 'VALID_AUTO'
                    self.save()
                    return True
                else:
                    # no reference values were found whatsoever for
                    # those on the Column itself.
                    self.integrity_status = 'UNAVAILABLE_AUTO'
                    self.save()
                    return None
    
    def get_absolute_url(self):
        return reverse(
            'col_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'Column'}
        )


class ReferenceColumn(models.Model):
    """Records details on reference values scraped from HCUP documentation.
    
    Uses source, state, and year to be later matched with a Column record. 
    """
    source = models.ForeignKey('DataSource')
    state = models.ForeignKey('State')
    year = models.IntegerField(blank=False, null=False, db_index=True)
    name = models.CharField(max_length=200, blank=False, db_index=True)
    
    count_notnull = models.IntegerField(help_text='Count of non-null values.')
    count_null = models.IntegerField(help_text='Count of null values.')
    min = models.DecimalField(max_digits=50, decimal_places=6, blank=True, default=None, null=True)
    max = models.DecimalField(max_digits=50, decimal_places=6, blank=True, default=None, null=True)
    stddev_samp = models.DecimalField(max_digits=50, decimal_places=6, blank=True, default=None, null=True)
    mean = models.DecimalField(max_digits=50, decimal_places=6, blank=True, default=None, null=True)
    
    def __unicode__(self):
        return "<ReferenceColumn %s: %s %s %s %s>" % (self.pk, self.source, self.state.abbreviation, self.year, self.name)
    
    def get_absolute_url(self):
        return reverse(
            'djhcup_staging.views.obj_detail',
            kwargs={'obj_id': self.pk, 'obj_type': 'ReferenceColumn'}
        )
