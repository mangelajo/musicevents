from django_q.tasks import schedule
from django_q.models import Schedule
from .utils.riviera_sync import sync_riviera_events
from .utils.ticketmaster import sync_events_for_city as sync_ticketmaster_events

def schedule_daily_tasks():
    """
    Schedule daily tasks for syncing events from Riviera and Ticketmaster
    """
    # Schedule Riviera sync
    Schedule.objects.get_or_create(
        name='riviera_sync',
        defaults={
            'func': 'events.tasks.run_riviera_sync',
            'schedule_type': Schedule.DAILY,
        }
    )

    # Schedule Ticketmaster sync for Madrid
    Schedule.objects.get_or_create(
        name='ticketmaster_sync_madrid',
        defaults={
            'func': 'events.tasks.run_ticketmaster_sync',
            'args': '("Madrid",)',
            'schedule_type': Schedule.DAILY,
        }
    )

def run_riviera_sync():
    """
    Run the Riviera sync task
    """
    sync_riviera_events()

def run_ticketmaster_sync(city):
    """
    Run the Ticketmaster sync task for a specific city
    """
    sync_ticketmaster_events(city)