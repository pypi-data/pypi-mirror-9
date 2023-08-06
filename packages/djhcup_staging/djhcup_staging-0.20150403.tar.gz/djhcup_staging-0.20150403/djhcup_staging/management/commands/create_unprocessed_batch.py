from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings

from djhcup_staging import tasks

import logging

logger = logging.getLogger('default')


class Command(NoArgsCommand):

	def handle_noargs(self, **options):
		tasks.create_unprocessed_batch()