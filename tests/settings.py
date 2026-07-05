SETTINGS = {
    'DEBUG_PROPAGATE_EXCEPTIONS': True,
    'DATABASES': {'default': {'ENGINE': 'django.db.backends.sqlite3',
                  'NAME': ':memory:'}},
    'INSTALLED_APPS': (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'klingon',
        'tests',
        'tests.testapp',
    ),
    'SITE_ID': 1,
    'SECRET_KEY': 'this-is-just-for-tests-so-not-that-secret',
    'LANGUAGES': (
        ('en', 'English'),
        ('pt_br', 'Brazilian Portuguese'),
        ('es', 'Spanish'),
    ),
    'MIDDLEWARE': (),
    'ROOT_URLCONF': 'tests.urls',
}
