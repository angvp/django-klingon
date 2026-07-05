import datetime

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.test import TestCase

from klingon.admin import TranslationInlineForm, create_translations
from klingon.models import Translation

from .testapp.models import Book


class CreateTranslationsActionTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )

    def tearDown(self):
        cache.clear()

    def test_create_translations_action_creates_translations(self):
        self.assertEqual(Translation.objects.count(), 0)

        create_translations(None, None, Book.objects.all())

        # translatable_fields plus the translatable_slug, for every language
        fields_count = len(self.book.translatable_fields) + 1
        self.assertEqual(
            Translation.objects.count(),
            len(settings.LANGUAGES) * fields_count,
        )


class TranslationInlineFormTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )
        self.book.translate()
        self.content_type = ContentType.objects.get_for_model(Book)

    def tearDown(self):
        cache.clear()

    def _get_translation(self, field):
        return Translation.objects.get(
            content_type=self.content_type,
            object_id=self.book.pk,
            lang='es',
            field=field,
        )

    def test_widget_swapped_to_text_input_for_char_field(self):
        trans = self._get_translation('title')
        form = TranslationInlineForm(instance=trans)
        self.assertIsInstance(form.fields['translation'].widget, forms.TextInput)

    def test_widget_swapped_to_textarea_for_text_field(self):
        trans = self._get_translation('description')
        form = TranslationInlineForm(instance=trans)
        self.assertIsInstance(form.fields['translation'].widget, forms.Textarea)

    def test_widget_not_swapped_for_slug_field(self):
        # SlugField is neither keyed by name nor by internal type in the
        # widgets mapping, so it keeps the ModelForm default: since
        # Translation.translation is a TextField, that default is Textarea.
        trans = self._get_translation('slug')
        form = TranslationInlineForm(instance=trans)
        self.assertIs(type(form.fields['translation'].widget), forms.Textarea)

    def test_init_without_instance_content_type_does_not_raise(self):
        form = TranslationInlineForm()
        self.assertIsInstance(form.fields['translation'].widget, forms.Textarea)


class TranslationInlineFormCleanTranslationTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Raven",
            description="The Raven is a narrative poem",
            publication_date=datetime.date(1845, 1, 1),
            slug="the-raven",
        )
        self.book.translate()
        self.content_type = ContentType.objects.get_for_model(Book)

    def tearDown(self):
        cache.clear()

    def _get_translation(self, field):
        return Translation.objects.get(
            content_type=self.content_type,
            object_id=self.book.pk,
            lang='es',
            field=field,
        )

    def _data_for(self, trans, translation):
        return {
            'content_type': self.content_type.pk,
            'object_id': trans.object_id,
            'lang': trans.lang,
            'field': trans.field,
            'translation': translation,
        }

    def test_translation_longer_than_max_length_is_invalid(self):
        trans = self._get_translation('title')
        data = self._data_for(trans, 'x' * 101)  # title max_length is 100

        form = TranslationInlineForm(data=data, instance=trans)

        self.assertFalse(form.is_valid())
        self.assertIn('translation', form.errors)
        self.assertIn('too long', form.errors['translation'][0])

    def test_translation_within_max_length_is_valid(self):
        trans = self._get_translation('title')
        data = self._data_for(trans, 'A short title')

        form = TranslationInlineForm(data=data, instance=trans)

        self.assertTrue(form.is_valid())

    def test_translation_length_check_skipped_when_no_max_length(self):
        trans = self._get_translation('description')
        data = self._data_for(trans, 'x' * 10000)  # TextField has no max_length

        form = TranslationInlineForm(data=data, instance=trans)

        self.assertTrue(form.is_valid())

    def test_translation_without_content_object_is_invalid(self):
        orphan = Translation(
            content_type=self.content_type,
            object_id=99999,
            lang='es',
            field='title',
        )
        data = self._data_for(orphan, 'Some translation')

        form = TranslationInlineForm(data=data, instance=orphan)

        self.assertFalse(form.is_valid())
        self.assertIn('translation', form.errors)
        self.assertIn(
            'First create all translation', form.errors['translation'][0]
        )
