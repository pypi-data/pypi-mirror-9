from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, port=8000, *args, **options):
        management.call_command('runserver', '0.0.0.0:{}'.format(port), *args, **options)
