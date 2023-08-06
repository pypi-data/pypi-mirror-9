from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from djhcup_staging import tasks

import logging


logger = logging.getLogger('default')

class Command(BaseCommand):

	ALLOWED_BATCH_TYPES = [
			'import',
			'staging'
	]
	
	def handle(self, obj_type, obj_id, *args, **options):

		obj_type = obj_type.lower()
		obj_id = int(obj_id)

		if obj_type not in self.ALLOWED_BATCH_TYPES:
			raise Exception("Requested batch type {t} not in allowed types: {a}" \
			.format(t=obj_type, a=self.ALLOWED_BATCH_TYPES))
	
		if obj_type == 'import':
			logger.info('Attempting to call a Celery task for ImportBatch %i' % (int(obj_id)))
			tresult = tasks.batch_import.delay(obj_id)
			logger.info("ImportBatch has been dispatched to Celery in thread %s." % (tresult))
		
		elif obj_type == 'staging':
			logger.info('Attempting to call a Celery task for StagingBatch %i' % (int(obj_id)))
			tresult = tasks.batch_stage.delay(obj_id)
			logger.info("StagingBatch has been dispatched to Celery in thread %s." % (tresult))