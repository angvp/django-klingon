import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.text import slugify
from klingon.models import Translation

from .testapp.models import Book


class CommandsTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )
        self.es_title = u"El Cuervo"
        self.es_description = 'El Cuervo es un poema narrativo'
        self.es_slug = slugify(self.es_title)

    def tearDown(self):
        # Remove cache after each test
        cache.clear()

    def _test_translate_models_command(self, args):
        args = args
        opts = {}
        call_command('translatemodels', *args, **opts)

    def test_translate_models_command_success(self):
        self._test_translate_models_command(['testapp.Book'])

        ifslug = 0
        if self.book.translatable_slug:
            ifslug = 1

        self.assertEqual(
            Translation.objects.count(),
            len(settings.LANGUAGES * (len(self.book.translatable_fields) + ifslug)),
        )

    def test_translate_models_command_empty(self):
        self._test_translate_models_command([])
        self.assertEqual(Translation.objects.count(), 0)

    def test_translate_models_command_wrong_args(self):
        self.assertRaises(
            CommandError,
            self._test_translate_models_command,
            ['wrong.argument']
        )
