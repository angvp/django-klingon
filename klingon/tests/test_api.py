import datetime
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from testapp.models import Book
from klingon.models import Translation, CanNotTranslate


class TranslationAPITestCase(TestCase):
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
        self.assertEquals(
            self.book.translations('es'),
            {
                'title': self.es_title,
                'description': self.es_description,
            }
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

    def test_translations(self):
        # translate book to spanish
        self.book.set_translation('es', 'title', self.es_title)
        self.book.set_translation('es', 'description', self.es_description)
        # get all spanish translations for the book
        self.assertEquals(
            self.book.translations('es'),
            {'title': self.es_title, 'description': self.es_description}
        )

    def test_translations_cache(self):
        # translate book to spanish
        self.book.set_translation('es', 'title', self.es_title)
        self.book.set_translation('es', 'description', self.es_description)
        # get translations
        trans = self.book.translations('es')
        # set a new translation
        es_new_title = 'El Cuervo (*)'
        self.book.set_translation('es', 'title', es_new_title)
        # get new translations
        new_trans = self.book.translations('es')
        self.assertNotEquals(trans, new_trans)
        self.assertEquals(
            new_trans,
            {'title': es_new_title, 'description': self.es_description}
        )

    @override_settings(KLINGON_DEFAULT_LANGUAGE='en')
    def test_create_translations_with_default_language(self):
        self.book.translate()
        self.assertEquals(
            len(Translation.objects.all()),
            (len(settings.LANGUAGES)-1)*len(self.book.translatable_fields)
        )
        # nothing should happen if you run translate tiwce
        self.book.translate()
        self.assertEquals(
            len(Translation.objects.all()),
            (len(settings.LANGUAGES)-1)*len(self.book.translatable_fields),
        )

    @override_settings(KLINGON_DEFAULT_LANGUAGE='en')
    def test_get_translation_with_default_language(self):
        es_title = self.book.get_translation('es', 'title')
        # Get should not create empty translations
        self.assertEquals(Translation.objects.count(), 0)
        # Get should fall back to default language
        self.assertEquals(es_title, self.book.title)

    @override_settings(KLINGON_DEFAULT_LANGUAGE='en')
    def test_set_translation_with_default_language(self):
        # Verify that there are no translations
        self.assertEquals(Translation.objects.count(), 0)
        # Create a translation
        self.book.set_translation('es', 'title', self.es_title)
        # Get should work as expected
        self.assertEquals(
            self.es_title,
            self.book.get_translation('es', 'title')
        )
        # Verify that only one translation was created
        self.assertEquals(Translation.objects.count(), 1)

    @override_settings(KLINGON_DEFAULT_LANGUAGE='en')
    def test_set_translation_in_default_language(self):
        # Create a translation for default language
        self.assertRaises(
            CanNotTranslate,
            self.book.set_translation,
            'en', 'title', 'The Raven!'
        )
