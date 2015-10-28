#!/usr/bin/env python
import sys

import django
from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'autoslug',
            'klingon.tests.testapp',
            'klingon',
        ),
        SITE_ID=1,
        SECRET_KEY='this-is-just-for-tests-so-not-that-secret',
        LANGUAGES = (
            ('en', 'English'),
            ('pt_br', 'Brazilian Portuguese'),
            ('es', 'Spanish'),
        ),
        MIDDLEWARE_CLASSES=(),
    )


from django.test.utils import get_runner
try:
    from django import setup
    setup()
except ImportError:
    pass


def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    apps = ['klingon', ]
    failures = test_runner.run_tests(apps)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
