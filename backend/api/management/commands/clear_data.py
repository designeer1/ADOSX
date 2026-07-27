from django.core.management.base import BaseCommand
from api.models import SystemARecord, SystemBRecord, Location, ComparisonResult

class Command(BaseCommand):
    help = 'Clear all data from the database'

    def handle(self, *args, **options):
        SystemARecord.objects.all().delete()
        SystemBRecord.objects.all().delete()
        Location.objects.all().delete()
        ComparisonResult.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All data cleared successfully'))