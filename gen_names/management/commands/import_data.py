"""
Django management command to import poetry and surname data
"""
from django.core.management.base import BaseCommand
from gen_names.data_processor import PoetryDataProcessor


class Command(BaseCommand):
    help = 'Import poetry, words, and surname data into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--poetry-only',
            action='store_true',
            help='Import only poetry data',
        )
        parser.add_argument(
            '--words-only',
            action='store_true',
            help='Import only word data',
        )
        parser.add_argument(
            '--surnames-only',
            action='store_true',
            help='Import only surname data',
        )

    def handle(self, *args, **options):
        processor = PoetryDataProcessor()

        if options['poetry_only']:
            self.stdout.write('Importing poetry data...')
            processor.import_poetry_data()
            self.stdout.write(self.style.SUCCESS('Poetry data imported successfully'))
        elif options['words_only']:
            self.stdout.write('Importing word data...')
            processor.import_word_data()
            self.stdout.write(self.style.SUCCESS('Word data imported successfully'))
        elif options['surnames_only']:
            self.stdout.write('Importing surname data...')
            processor.import_surname_data()
            self.stdout.write(self.style.SUCCESS('Surname data imported successfully'))
        else:
            self.stdout.write('Importing all data...')
            processor.process_all_data()
            self.stdout.write(self.style.SUCCESS('All data imported successfully'))