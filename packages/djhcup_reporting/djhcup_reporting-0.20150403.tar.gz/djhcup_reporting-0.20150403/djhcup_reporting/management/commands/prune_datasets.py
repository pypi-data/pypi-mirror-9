from django.core.management.base import NoArgsCommand

from djhcup_reporting import tasks


class Command(NoArgsCommand):
	
	def handle_noargs(self, **options):
		tasks.discover_files()
