from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Configure the Django Site domain for OAuth'

    def handle(self, *args, **kwargs):
        hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:8000')
        site = Site.objects.get_current()
        site.domain = hostname
        site.name = 'BrightTrack LMS'
        site.save()
        self.stdout.write(f'✅ Site domain set to: {hostname}')
