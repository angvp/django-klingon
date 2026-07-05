import datetime
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from django.utils.text import slugify

from klingon.models import CanNotTranslate, Translatable, Translation

from .testapp.models import Book, Library


class TranslationStrTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )

    def tearDown(self):
        cache.clear()

    def test_translation_str(self):
        self.book.translate()

        trans = Translation.objects.get(lang='es', field='title')

        self.assertEqual(
            str(trans),
            f'{self.book} : es : title',
        )


class TranslationsObjectsTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )

    def tearDown(self):
        cache.clear()

    def test_translations_objects_returns_only_that_language(self):
        self.book.translate()

        es_translations = self.book.translations_objects('es')

        # translatable_fields ('title', 'description') plus the slug
        self.assertEqual(es_translations.count(), 3)
        for trans in es_translations:
            self.assertEqual(trans.lang, 'es')


class TranslationsLinkTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )

    def tearDown(self):
        cache.clear()

    def test_translations_link(self):
        content_type = ContentType.objects.get_for_model(Book)

        expected_url = (
            reverse('admin:klingon_translation_changelist')
            + f'?content_type__id__exact={content_type.id}&object_id={self.book.pk}'
        )

        self.assertEqual(
            self.book.translations_link(),
            f'<a href="{escape(expected_url)}">translate</a>',
        )


class GetTranslationObjTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )

    def tearDown(self):
        cache.clear()

    def test_create_true_creates_missing_translation(self):
        self.assertEqual(Translation.objects.count(), 0)

        trans = self.book.get_translation_obj('es', 'title', create=True)

        self.assertIsNotNone(trans)
        self.assertIsNone(trans.translation)
        self.assertEqual(Translation.objects.count(), 1)

    def test_returns_existing_translation(self):
        self.book.set_translation('es', 'title', 'El Cuervo')

        trans = self.book.get_translation_obj('es', 'title', create=True)

        self.assertEqual(trans.translation, 'El Cuervo')

    def test_create_false_returns_none_when_missing(self):
        trans = self.book.get_translation_obj('es', 'title', create=False)

        self.assertIsNone(trans)
        self.assertEqual(Translation.objects.count(), 0)


class CacheHitTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )
        self.book.set_translation('es', 'title', 'El Cuervo')
        self.book.set_translation('es', 'description', 'El Cuervo es un poema')
        self.book.set_translation('es', 'slug', slugify('El Cuervo'))

    def tearDown(self):
        cache.clear()

    def test_get_translation_second_call_hits_cache(self):
        self.book.get_translation('es', 'title')

        with self.assertNumQueries(0):
            self.book.get_translation('es', 'title')

    def test_translations_second_call_hits_cache(self):
        self.book.translations('es')

        with self.assertNumQueries(0):
            self.book.translations('es')


class AutoslugDisabledTestCase(TestCase):
    def setUp(self):
        self.library = Library.objects.create(
            name="Indepent",
            description="All in ebooks",
        )

    def tearDown(self):
        cache.clear()

    def test_set_translation_does_not_touch_slug_when_autoslug_disabled(self):
        with mock.patch('klingon.models.INSTALLED_AUTOSLUG', False):
            self.library.set_translation('es', 'name', 'Independiente')

        slug_trans = Translation.objects.get(lang='es', field='slug')
        self.assertFalse(slug_trans.translation)


class UnsavedInstanceGuardTestCase(TestCase):
    def tearDown(self):
        cache.clear()

    def test_translate_raises_for_unsaved_instance(self):
        book = Book()

        self.assertRaises(CanNotTranslate, book.translate)

    def test_set_translation_raises_for_unsaved_instance(self):
        book = Book()

        self.assertRaises(
            CanNotTranslate,
            book.set_translation,
            'es', 'title', 'x',
        )

    def test_get_translation_obj_create_raises_for_unsaved_instance(self):
        book = Book()

        self.assertRaises(
            CanNotTranslate,
            book.get_translation_obj,
            'es', 'title', True,
        )

    def test_get_translation_no_cache_bleed_between_unsaved_instances(self):
        book_a = Book(title='Alpha')
        book_b = Book(title='Beta')

        self.assertEqual(book_a.get_translation('es', 'title'), 'Alpha')
        self.assertEqual(book_b.get_translation('es', 'title'), 'Beta')
        # calling again (order reversed) must still be instance-specific
        self.assertEqual(book_b.get_translation('es', 'title'), 'Beta')
        self.assertEqual(book_a.get_translation('es', 'title'), 'Alpha')

        self.assertEqual(Translation.objects.count(), 0)

    def test_translations_no_cache_bleed_between_unsaved_instances(self):
        book_a = Book(title='Alpha')
        book_b = Book(title='Beta')

        self.assertEqual(book_a.translations('es')['title'], 'Alpha')
        self.assertEqual(book_b.translations('es')['title'], 'Beta')

        self.assertEqual(Translation.objects.count(), 0)


class AllTranslatableFieldsMutationTestCase(TestCase):
    """
    Bug: _all_translatable_fields() aliased a list-typed translatable_fields
    class attribute and mutated it in place via `+=`.
    """

    def tearDown(self):
        cache.clear()

    def test_list_translatable_fields_not_mutated(self):
        class LocalTranslatable(Translatable):
            translatable_fields = ['title', 'description']
            translatable_slug = 'slug'

        instance = LocalTranslatable()

        instance._all_translatable_fields()
        instance._all_translatable_fields()

        self.assertEqual(
            LocalTranslatable.translatable_fields,
            ['title', 'description'],
        )
