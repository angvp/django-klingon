
import pytest
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from klingon.admin import TranslationInlineForm, create_translations
from klingon.models import Translation

from .testapp.models import Book


# Helper functions for test_admin.py
def get_translation(book, field, lang='es'):
    """Helper: fetch a Translation object by field and language."""
    content_type = ContentType.objects.get_for_model(Book)
    return Translation.objects.get(
        content_type=content_type,
        object_id=book.pk,
        lang=lang,
        field=field,
    )


def data_for_translation_form(trans, translation):
    """Helper: build form data dict for TranslationInlineForm."""
    content_type = ContentType.objects.get_for_model(Book)
    return {
        'content_type': content_type.pk,
        'object_id': trans.object_id,
        'lang': trans.lang,
        'field': trans.field,
        'translation': translation,
    }


# Fixtures
@pytest.fixture
def book_with_translations(book, db):
    """Book with translations already created via book.translate()."""
    book.translate()
    return book


# Tests: CreateTranslationsActionTestCase
@pytest.mark.django_db
def test_create_translations_action_creates_translations(book):
    """Test create_translations admin action creates translations for all languages."""
    assert Translation.objects.count() == 0

    create_translations(None, None, Book.objects.all())

    # translatable_fields plus the translatable_slug, for every language
    fields_count = len(book.translatable_fields) + 1
    assert Translation.objects.count() == len(settings.LANGUAGES) * fields_count


# Tests: TranslationInlineFormTestCase
@pytest.mark.django_db
def test_widget_swapped_to_text_input_for_char_field(book_with_translations):
    """Test that TextInput widget is used for CharField translations."""
    trans = get_translation(book_with_translations, 'title')
    form = TranslationInlineForm(instance=trans)
    assert isinstance(form.fields['translation'].widget, forms.TextInput)


@pytest.mark.django_db
def test_widget_swapped_to_textarea_for_text_field(book_with_translations):
    """Test that Textarea widget is used for TextField translations."""
    trans = get_translation(book_with_translations, 'description')
    form = TranslationInlineForm(instance=trans)
    assert isinstance(form.fields['translation'].widget, forms.Textarea)


@pytest.mark.django_db
def test_widget_not_swapped_for_slug_field(book_with_translations):
    """Test that SlugField translations keep default Textarea widget.

    SlugField is neither keyed by name nor by internal type in the
    widgets mapping, so it keeps the ModelForm default: since
    Translation.translation is a TextField, that default is Textarea.
    """
    trans = get_translation(book_with_translations, 'slug')
    form = TranslationInlineForm(instance=trans)
    assert type(form.fields['translation'].widget) is forms.Textarea


@pytest.mark.django_db
def test_init_without_instance_content_type_does_not_raise():
    """Test that TranslationInlineForm initializes without an instance."""
    form = TranslationInlineForm()
    assert isinstance(form.fields['translation'].widget, forms.Textarea)


# Tests: TranslationInlineFormCleanTranslationTestCase
@pytest.mark.django_db
def test_translation_longer_than_max_length_is_invalid(book_with_translations):
    """Test that translations exceeding max_length are rejected."""
    trans = get_translation(book_with_translations, 'title')
    data = data_for_translation_form(trans, 'x' * 101)  # title max_length is 100

    form = TranslationInlineForm(data=data, instance=trans)

    assert not form.is_valid()
    assert 'translation' in form.errors
    assert 'too long' in form.errors['translation'][0]


@pytest.mark.django_db
def test_translation_within_max_length_is_valid(book_with_translations):
    """Test that translations within max_length are accepted."""
    trans = get_translation(book_with_translations, 'title')
    data = data_for_translation_form(trans, 'A short title')

    form = TranslationInlineForm(data=data, instance=trans)

    assert form.is_valid()


@pytest.mark.django_db
def test_translation_length_check_skipped_when_no_max_length(book_with_translations):
    """Test that TextField translations skip max_length validation."""
    trans = get_translation(book_with_translations, 'description')
    data = data_for_translation_form(trans, 'x' * 10000)  # TextField has no max_length

    form = TranslationInlineForm(data=data, instance=trans)

    assert form.is_valid()


@pytest.mark.django_db
def test_translation_without_content_object_is_invalid(book_with_translations):
    """Test that orphaned translations (object_id doesn't exist) are rejected."""
    content_type = ContentType.objects.get_for_model(Book)
    orphan = Translation(
        content_type=content_type,
        object_id=99999,
        lang='es',
        field='title',
    )
    data = data_for_translation_form(orphan, 'Some translation')

    form = TranslationInlineForm(data=data, instance=orphan)

    assert not form.is_valid()
    assert 'translation' in form.errors
    assert 'First create all translation' in form.errors['translation'][0]
