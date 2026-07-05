"""
Regression tests for cache/auto-slug bugs found in the 0.1.0 revival review.
"""
from django.core.cache import cache
from django.test import TestCase

from klingon.models import Translation

from .testapp.models import Library


class SlugCacheInvalidationTestCase(TestCase):
    """
    Bug 1: set_translation() on the slug's source field regenerated the slug
    Translation row but never refreshed the slug's per-field cache key, so
    get_translation() kept serving the stale pre-translation value.
    """

    def setUp(self):
        self.library = Library.objects.create(
            name="Independent",
            description="All in ebooks",
        )

    def tearDown(self):
        cache.clear()

    def test_slug_cache_refreshed_after_source_field_translation(self):
        # Prime the per-field cache with the fallback (English) slug
        self.assertEqual(
            self.library.get_translation('es', 'slug'),
            'independent',
        )
        # Translating the source field regenerates the slug translation
        self.library.set_translation('es', 'name', 'Independiente')
        db_value = Translation.objects.get(lang='es', field='slug').translation
        self.assertEqual(db_value, 'independiente')
        # The API must agree with the database, not the stale cache
        self.assertEqual(self.library.get_translation('es', 'slug'), db_value)


class ExplicitSlugTranslationTestCase(TestCase):
    """
    Bug 2: set_translation() on the slug field itself saved the given text,
    then the auto-slug block immediately overwrote the same row with
    slugify(<title_field translation>) — losing the explicit value and
    leaving the cache disagreeing with the database.
    """

    def setUp(self):
        self.library = Library.objects.create(
            name="Independent",
            description="All in ebooks",
        )

    def tearDown(self):
        cache.clear()

    def test_explicit_slug_translation_is_kept(self):
        self.library.set_translation('es', 'name', 'Independiente')
        self.library.set_translation('es', 'slug', 'mi-slug-custom')
        db_value = Translation.objects.get(lang='es', field='slug').translation
        self.assertEqual(db_value, 'mi-slug-custom')

    def test_explicit_slug_translation_cache_matches_db(self):
        self.library.set_translation('es', 'name', 'Independiente')
        self.library.set_translation('es', 'slug', 'mi-slug-custom')
        db_value = Translation.objects.get(lang='es', field='slug').translation
        self.assertEqual(self.library.get_translation('es', 'slug'), db_value)
