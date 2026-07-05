import pytest
from django.conf import settings
from django.test.utils import override_settings
from django.utils.text import slugify

from klingon.models import CanNotTranslate, Translation

from .testapp.models import Library

# ============================================================================
# TranslationAPITestCase tests (migrated to pytest functions)
# ============================================================================


@pytest.mark.django_db
def test_api_general_usage(book):
    """Test basic set/get translation API."""
    es_title = "El Cuervo"
    es_description = 'El Cuervo es un poema narrativo'
    es_slug = slugify(es_title)
    # translate book to spanish
    book.set_translation('es', 'title', es_title)
    book.set_translation('es', 'description', es_description)
    book.set_translation('es', 'slug', es_slug)
    # Get translations
    assert book.get_translation('es', 'title') == es_title
    assert book.get_translation('es', 'description') == es_description
    assert book.get_translation('es', 'slug') == es_slug
    assert book.translations('es') == {
        'title': es_title,
        'description': es_description,
        'slug': es_slug,
    }


@pytest.mark.django_db
def test_api_default_value(book):
    """Test that untranslated fields fall back to default values."""
    assert book.get_translation('es', 'title') == book.title
    assert book.get_translation('es', 'description') == book.description
    assert book.get_translation('es', 'slug') == book.slug


@pytest.mark.django_db
def test_create_translations(book):
    """Test translate() creates translations for all languages."""
    book.translate()

    # translatable_fields plus the translatable_slug
    fields_count = len(book.translatable_fields) + 1
    assert Translation.objects.count() == len(settings.LANGUAGES) * fields_count

    # nothing should happen if you run translate twice
    book.translate()

    assert Translation.objects.count() == len(settings.LANGUAGES) * fields_count


@pytest.mark.django_db
def test_set_translation(book):
    """Test set_translation creates a Translation object."""
    es_title = "El Cuervo"
    book.set_translation('es', 'title', es_title)
    assert Translation.objects.get(lang='es', field='title').translation == es_title


@pytest.mark.django_db
def test_get_translation(book):
    """Test get_translation retrieves stored translations."""
    es_title = "El Cuervo"
    book.set_translation('es', 'title', es_title)
    retrieved_title = book.get_translation('es', 'title')
    assert retrieved_title == es_title


@pytest.mark.django_db
def test_translations(book):
    """Test translations() returns all translations for a language."""
    es_title = "El Cuervo"
    es_description = 'El Cuervo es un poema narrativo'
    es_slug = slugify(es_title)
    # translate book to spanish
    book.set_translation('es', 'title', es_title)
    book.set_translation('es', 'description', es_description)
    book.set_translation('es', 'slug', es_slug)
    # get all spanish translations for the book
    assert book.translations('es') == {
        'title': es_title,
        'description': es_description,
        'slug': es_slug,
    }


@pytest.mark.django_db
def test_translations_cache(book):
    """Test that cache is properly invalidated on translation changes."""
    es_title = "El Cuervo"
    es_description = 'El Cuervo es un poema narrativo'
    es_slug = slugify(es_title)
    # translate book to spanish
    book.set_translation('es', 'title', es_title)
    book.set_translation('es', 'description', es_description)
    book.set_translation('es', 'slug', es_slug)
    # get translations
    trans = book.translations('es')
    # set a new translation
    es_new_title = 'El Cuervo (*)'
    book.set_translation('es', 'title', es_new_title)
    # get new translations
    new_trans = book.translations('es')
    assert trans != new_trans
    assert new_trans == {
        'title': es_new_title,
        'description': es_description,
        'slug': es_slug,
    }


@pytest.mark.django_db
@override_settings(KLINGON_DEFAULT_LANGUAGE='en')
def test_create_translations_with_default_language(book):
    """Test translate() excludes translations in default language."""
    book.translate()

    # translatable_fields plus the translatable_slug
    fields_count = len(book.translatable_fields) + 1
    expected = (len(settings.LANGUAGES) - 1) * fields_count
    assert len(Translation.objects.all()) == expected

    # nothing should happen if you run translate twice
    book.translate()
    assert len(Translation.objects.all()) == expected


@pytest.mark.django_db
@override_settings(KLINGON_DEFAULT_LANGUAGE='en')
def test_get_translation_with_default_language(book):
    """Test get_translation with default language excludes default lang translations."""
    es_title = book.get_translation('es', 'title')
    # Get should not create empty translations
    assert Translation.objects.count() == 0
    # Get should fall back to default language
    assert es_title == book.title


@pytest.mark.django_db
@override_settings(KLINGON_DEFAULT_LANGUAGE='en')
def test_set_translation_with_default_language(book):
    """Test set_translation with default language excludes default language."""
    es_title = "El Cuervo"
    # Verify that there are no translations
    assert Translation.objects.count() == 0
    # Create a translation
    book.set_translation('es', 'title', es_title)
    # Get should work as expected
    assert es_title == book.get_translation('es', 'title')
    # Verify that only one translation was created
    assert Translation.objects.count() == 1


@pytest.mark.django_db
@override_settings(KLINGON_DEFAULT_LANGUAGE='en')
def test_set_translation_in_default_language(book):
    """Test that setting translation in default language raises error."""
    with pytest.raises(CanNotTranslate):
        book.set_translation('en', 'title', 'The Raven!')


# ============================================================================
# AutomaticTranslationAPITestCase tests (migrated to pytest functions)
# ============================================================================


@pytest.mark.django_db
def test_translation_created_automatically(db):
    """Test that translations are created automatically on save."""
    library = Library.objects.create(
        name="Indepent",
        description="All in ebooks",
    )
    # translatable_fields plus the translatable_slug
    fields_count = len(library.translatable_fields) + 1
    assert len(Translation.objects.all()) == len(settings.LANGUAGES) * fields_count


@pytest.mark.django_db
def test_translation_slug(db):
    """Test that slug translation works correctly."""
    es_name = "Independiente"
    es_description = 'Todo en ebooks'
    es_slug = slugify(es_name)

    library = Library.objects.create(
        name="Indepent",
        description="All in ebooks",
    )
    library.set_translation('es', 'name', es_name)
    library.set_translation('es', 'description', es_description)
    assert library.slug == slugify(library.name)
    assert library.get_translation('es', 'name') == es_name
    assert library.get_translation('es', 'slug') == es_slug
