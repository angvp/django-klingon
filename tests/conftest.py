import datetime

import pytest
from django.core.cache import cache


def pytest_configure():
    from django.conf import settings
    if not settings.configured:
        from tests.settings import SETTINGS
        settings.configure(**SETTINGS)

        try:
            import django
            django.setup()
        except AttributeError:
            pass


@pytest.fixture(scope='function')
def book(db):
    """Standard Book instance with test data for isolation testing.

    Provides a clean Book instance for each test function with:
    - title="The Raven"
    - description="The Raven is a narrative poem"
    - publication_date=1845-01-01
    - slug="the-raven"
    """
    from tests.testapp.models import Book
    return Book.objects.create(
        title="The Raven",
        description="The Raven is a narrative poem",
        publication_date=datetime.date(1845, 1, 1),
        slug="the-raven"
    )


@pytest.fixture(scope='function')
def library(db):
    """Standard Library instance for isolation testing.

    Provides a clean Library instance for each test function with:
    - name="Independent"
    - description="All in ebooks"
    """
    from tests.testapp.models import Library
    return Library.objects.create(
        name="Independent",
        description="All in ebooks",
    )


@pytest.fixture(autouse=True)
def clear_cache():
    """Auto-clear Django cache after each test.

    Ensures cache state doesn't leak between tests. This fixture runs
    automatically (autouse=True) after every test, yielding first and
    then clearing the cache for cleanup.
    """
    yield
    cache.clear()
