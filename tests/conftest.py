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
