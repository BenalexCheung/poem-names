"""
Django management command to wait for database to be available
"""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Wait for database to be available'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Timeout in seconds',
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Try to connect to the database
                connections['default'].cursor()
                self.stdout.write(self.style.SUCCESS('Database is available'))
                return
            except OperationalError:
                self.stdout.write('Waiting for database...')
                time.sleep(1)

        self.stderr.write(self.style.ERROR('Database connection timeout'))
        exit(1)