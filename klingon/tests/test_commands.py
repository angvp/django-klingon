import datetime
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from testapp.models import Book
from klingon.models import Translation


class CommandsTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1)
        )
        self.es_title = 'El Cuervo'
        self.es_description = 'El Cuervo es un poema narrativo'

    def tearDown(self):
        # Remove cache after each test
        cache.clear()

    def test_translate_models_command(self):
        args = ['testapp.Book']
        opts = {}
        call_command('translatemodels', *args, **opts)
        self.assertEquals(
            len(Translation.objects.all()),
            len(settings.LANGUAGES*len(self.book.translatable_fields)),
        )
