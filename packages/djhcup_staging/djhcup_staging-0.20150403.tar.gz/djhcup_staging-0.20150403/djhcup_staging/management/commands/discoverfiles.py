from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings

from djhcup_staging import tasks

import pyhcup

import logging

logger = logging.getLogger('default')

class Command(NoArgsCommand):
	
	def handle_noargs(self, **options):
		tasks.discover_files()