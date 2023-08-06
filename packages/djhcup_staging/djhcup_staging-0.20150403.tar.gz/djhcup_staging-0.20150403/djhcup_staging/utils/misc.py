# local project and app packages
import datetime
import psycopg2

from django.db.models import Q
from django.conf import settings

from djhcup_staging.models import File, ImportQueue, ImportBatch, StagingQueue, StagingBatch, StagingTable, DataSource


def dead_batches():
    # grab queryset for batches started but not completed
    inc_batch_qs = ImportBatch.objects.filter(start__isnull=False, complete__isnull=True)
    
    # need this object to check task status
    from celery.result import AsyncResult
    
    # filter down to those which are ongoing, as determined by an active (ready()==False) celery task
    wip_batch_qs = inc_batch_qs.filter(
        pk__in=(b.pk for b in inc_batch_qs if not AsyncResult(b.celery_task_id).ready())
        )
    
    # exclude the ongoing batches from the total incomplete batches
    # this generates the queryset of dead batches
    dead_batch_qs = inc_batch_qs.exclude(pk__in=[b.pk for b in wip_batch_qs])
    
    return dead_batch_qs


def years():
    vl = File.objects \
        .values_list('year', flat=True) \
        .order_by('year') \
        .distinct('year')
    return vl


def states():
    vl = File.objects \
        .values_list('state__abbreviation', flat=True) \
        .order_by('state__abbreviation') \
        .distinct('state__abbreviation')
    return vl


def get_pgcnxn():
    DB_DEF = settings.DATABASES['djhcup']
    cnxn = psycopg2.connect(
        host=DB_DEF['HOST'],
        port=DB_DEF['PORT'],
        user=DB_DEF['USER'],
        password=DB_DEF['PASSWORD'],
        database=DB_DEF['NAME'],
        )
    return cnxn
