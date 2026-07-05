"""
Regression tests for cache/auto-slug bugs found in the 0.1.0 revival review.
"""
import pytest

from klingon.models import Translation


@pytest.mark.django_db
def test_slug_cache_refreshed_after_source_field_translation(library):
    """
    Bug 1: set_translation() on the slug's source field regenerated the slug
    Translation row but never refreshed the slug's per-field cache key, so
    get_translation() kept serving the stale pre-translation value.
    """
    # Prime the per-field cache with the fallback (English) slug
    assert library.get_translation('es', 'slug') == 'independent'

    # Translating the source field regenerates the slug translation
    library.set_translation('es', 'name', 'Independiente')
    db_value = Translation.objects.get(lang='es', field='slug').translation
    assert db_value == 'independiente'

    # The API must agree with the database, not the stale cache
    assert library.get_translation('es', 'slug') == db_value


@pytest.mark.django_db
def test_explicit_slug_translation_is_kept(library):
    """
    Bug 2: set_translation() on the slug field itself saved the given text,
    then the auto-slug block immediately overwrote the same row with
    slugify(<title_field translation>) — losing the explicit value and
    leaving the cache disagreeing with the database.
    """
    library.set_translation('es', 'name', 'Independiente')
    library.set_translation('es', 'slug', 'mi-slug-custom')
    db_value = Translation.objects.get(lang='es', field='slug').translation
    assert db_value == 'mi-slug-custom'


@pytest.mark.django_db
def test_explicit_slug_translation_cache_matches_db(library):
    """
    Verify that explicit slug translations stay in sync between cache and database.
    """
    library.set_translation('es', 'name', 'Independiente')
    library.set_translation('es', 'slug', 'mi-slug-custom')
    db_value = Translation.objects.get(lang='es', field='slug').translation
    assert library.get_translation('es', 'slug') == db_value


@pytest.mark.django_db
def test_explicit_slug_survives_unrelated_field_translation(library):
    """
    Bug: the old gate regenerated the slug whenever the field being
    set was merely "not the slug", so translating an unrelated field
    (description, which is not the slug's source field) clobbered an
    explicit slug override.
    """
    library.set_translation('es', 'slug', 'mi-slug-custom')
    library.set_translation('es', 'description', 'Todo en ebooks')

    db_value = Translation.objects.get(lang='es', field='slug').translation
    assert db_value == 'mi-slug-custom'
    assert library.get_translation('es', 'slug') == db_value
