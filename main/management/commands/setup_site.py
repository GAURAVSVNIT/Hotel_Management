from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Set up the default site domain for password reset emails'

    def handle(self, *args, **options):
        site = Site.objects.get(id=1)
        site.domain = 'localhost:8000'  # For development
        site.name = 'DineEase'
        site.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully set up site: {site.name} ({site.domain})'
        ))

