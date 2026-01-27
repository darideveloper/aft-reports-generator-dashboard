from django.core.management.base import BaseCommand
from django.utils import timezone
from survey.models import FormProgress


class Command(BaseCommand):
    help = "Delete expired FormProgress records"

    def handle(self, *args, **options):
        now = timezone.now()
        deleted_count, _ = FormProgress.objects.filter(expires_at__lt=now).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {deleted_count} expired records")
        )
