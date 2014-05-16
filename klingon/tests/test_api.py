import datetime
from django.conf import settings
from django.test import TestCase
from testapp.models import Book
from klingon.models import Translation


class TranslationAPITestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1)
        )
        self.es_title = 'El Cuervo'
        self.es_description = 'El Cuervo es un poema narrativo'

    def test_api_general_usage(self):
        # translate book to spanish
        self.book.set_translation('es', 'title', self.es_title)
        self.book.set_translation('es', 'description', self.es_description)
        # Get translations
        self.assertEquals(
            self.book.get_translation('es', 'title'),
            self.es_title
        )
        self.assertEquals(
            self.book.get_translation('es', 'description'),
            self.es_description
        )

    def test_api_default_value(self):
        self.assertEquals(
            self.book.get_translation('es', 'title'),
            self.book.title
        )
        self.assertEquals(
            self.book.get_translation('es', 'description'),
            self.book.description
        )

    def test_create_translations(self):
        self.book.translate()
        self.assertEquals(
            len(Translation.objects.all()),
            len(settings.LANGUAGES*len(self.book.translatable_fields)),
        )
        # nothing should happen if you run translate tiwce
        self.book.translate()
        self.assertEquals(
            len(Translation.objects.all()),
            len(settings.LANGUAGES*len(self.book.translatable_fields)),
        )

    def test_set_translation(self):
        self.book.set_translation('es', 'title', self.es_title)
        self.assertEquals(
            Translation.objects.get(lang='es', field='title').translation,
            self.es_title
        )

    def test_get_translation(self):
        self.book.set_translation('es', 'title', self.es_title)
        es_title = self.book.get_translation('es', 'title')
        self.assertEquals(
            es_title,
            self.es_title
        )


