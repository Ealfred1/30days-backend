from django.core.management.base import BaseCommand
from django.utils import timezone
from versions.models import Version
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates a test version for the 30-day challenge'

    def handle(self, *args, **kwargs):
        # Deactivate any existing active versions
        Version.objects.filter(is_active=True).update(is_active=False)
        
        # Get the latest version number or start with 1
        latest_version = Version.objects.order_by('-number').first()
        new_version_number = (latest_version.number + 1) if latest_version else 1
        
        # Create new version
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        version = Version.objects.create(
            name=f'Challenge Edition {new_version_number}',
            number=new_version_number,
            description='30 Days of Code with VickyJay',
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Version "{version.name}" (v{version.number}) '
                f'from {start_date} to {end_date}'
            )
        )