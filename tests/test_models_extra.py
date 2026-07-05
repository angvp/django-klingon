import datetime

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.urls import reverse
from django.utils.html import escape
from django.utils.text import slugify

from klingon.models import CanNotTranslate, Translatable, Translation

from .testapp.models import Book, Library


@pytest.fixture
def book(db):
    """Create a basic Book instance."""
    return Book.objects.create(
        title="The Raven",
        description="The Raven is a narrative poem",
        publication_date=datetime.date(1845, 1, 1),
        slug="the-raven",
    )


@pytest.fixture
def library(db):
    """Create a basic Library instance."""
    return Library.objects.create(
        name="Indepent",
        description="All in ebooks",
    )


@pytest.fixture
def book_with_translations(book, db):
    """Create a book with Spanish translations pre-set."""
    book.set_translation('es', 'title', 'El Cuervo')
    book.set_translation('es', 'description', 'El Cuervo es un poema')
    book.set_translation('es', 'slug', slugify('El Cuervo'))
    return book


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear cache after each test."""
    yield
    cache.clear()


# TranslationStrTestCase


@pytest.mark.django_db
def test_translation_str(book):
    book.translate()

    trans = Translation.objects.get(lang='es', field='title')

    assert str(trans) == f'{book} : es : title'


# TranslationsObjectsTestCase


@pytest.mark.django_db
def test_translations_objects_returns_only_that_language(book):
    book.translate()

    es_translations = book.translations_objects('es')

    # translatable_fields ('title', 'description') plus the slug
    assert es_translations.count() == 3
    for trans in es_translations:
        assert trans.lang == 'es'


# TranslationsLinkTestCase


@pytest.mark.django_db
def test_translations_link(book):
    content_type = ContentType.objects.get_for_model(Book)

    expected_url = (
        reverse('admin:klingon_translation_changelist')
        + f'?content_type__id__exact={content_type.id}&object_id={book.pk}'
    )

    assert book.translations_link() == f'<a href="{escape(expected_url)}">translate</a>'


# GetTranslationObjTestCase


@pytest.mark.django_db
def test_create_true_creates_missing_translation(book):
    assert Translation.objects.count() == 0

    trans = book.get_translation_obj('es', 'title', create=True)

    assert trans is not None
    assert trans.translation is None
    assert Translation.objects.count() == 1


@pytest.mark.django_db
def test_returns_existing_translation(book):
    book.set_translation('es', 'title', 'El Cuervo')

    trans = book.get_translation_obj('es', 'title', create=True)

    assert trans.translation == 'El Cuervo'


@pytest.mark.django_db
def test_create_false_returns_none_when_missing(book):
    trans = book.get_translation_obj('es', 'title', create=False)

    assert trans is None
    assert Translation.objects.count() == 0


# CacheHitTestCase


@pytest.mark.django_db
def test_get_translation_second_call_hits_cache(
    book_with_translations, django_assert_num_queries
):
    book_with_translations.get_translation('es', 'title')

    with django_assert_num_queries(0):
        book_with_translations.get_translation('es', 'title')


@pytest.mark.django_db
def test_translations_second_call_hits_cache(
    book_with_translations, django_assert_num_queries
):
    book_with_translations.translations('es')

    with django_assert_num_queries(0):
        book_with_translations.translations('es')


# AutoslugDisabledTestCase


@pytest.mark.django_db
def test_set_translation_does_not_touch_slug_when_autoslug_disabled(
    library, monkeypatch
):
    monkeypatch.setattr('klingon.models.INSTALLED_AUTOSLUG', False)
    library.set_translation('es', 'name', 'Independiente')

    slug_trans = Translation.objects.get(lang='es', field='slug')
    assert not slug_trans.translation


# UnsavedInstanceGuardTestCase


@pytest.mark.django_db
def test_translate_raises_for_unsaved_instance():
    book = Book()

    with pytest.raises(CanNotTranslate):
        book.translate()


@pytest.mark.django_db
def test_set_translation_raises_for_unsaved_instance():
    book = Book()

    with pytest.raises(CanNotTranslate):
        book.set_translation('es', 'title', 'x')


@pytest.mark.django_db
def test_get_translation_obj_create_raises_for_unsaved_instance():
    book = Book()

    with pytest.raises(CanNotTranslate):
        book.get_translation_obj('es', 'title', True)


@pytest.mark.django_db
def test_get_translation_no_cache_bleed_between_unsaved_instances():
    book_a = Book(title='Alpha')
    book_b = Book(title='Beta')

    assert book_a.get_translation('es', 'title') == 'Alpha'
    assert book_b.get_translation('es', 'title') == 'Beta'
    # calling again (order reversed) must still be instance-specific
    assert book_b.get_translation('es', 'title') == 'Beta'
    assert book_a.get_translation('es', 'title') == 'Alpha'

    assert Translation.objects.count() == 0


@pytest.mark.django_db
def test_translations_no_cache_bleed_between_unsaved_instances():
    book_a = Book(title='Alpha')
    book_b = Book(title='Beta')

    assert book_a.translations('es')['title'] == 'Alpha'
    assert book_b.translations('es')['title'] == 'Beta'

    assert Translation.objects.count() == 0


# AllTranslatableFieldsMutationTestCase


@pytest.mark.django_db
def test_list_translatable_fields_not_mutated():
    """
    Bug: _all_translatable_fields() aliased a list-typed translatable_fields
    class attribute and mutated it in place via `+=`.
    """

    class LocalTranslatable(Translatable):
        translatable_fields = ['title', 'description']
        translatable_slug = 'slug'

    instance = LocalTranslatable()

    instance._all_translatable_fields()
    instance._all_translatable_fields()

    assert LocalTranslatable.translatable_fields == ['title', 'description']
