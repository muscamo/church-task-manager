# notifications/management/commands/check_overdue_tasks.py
from django.core.management.base import BaseCommand
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Check for overdue tasks and create notifications'

    def handle(self, *args, **options):
        count = Notification.create_overdue_notifications()
        self.stdout.write(
            self.style.SUCCESS(f'Created {count} overdue task notifications')
        )
