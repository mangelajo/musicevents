from django.core.management.base import BaseCommand
from events.tasks import schedule_daily_tasks

class Command(BaseCommand):
    help = 'Set up scheduled tasks for event synchronization'

    def handle(self, *args, **options):
        schedule_daily_tasks()
        self.stdout.write(self.style.SUCCESS('Successfully set up scheduled tasks'))