from django.apps import AppConfig


class KlingonConfig(AppConfig):
    name = 'klingon'
    # Pin to the historical AutoField so existing installs are not forced
    # into an unrequested PK-type migration now that Django 6.0 changed the
    # global DEFAULT_AUTO_FIELD default to BigAutoField.
    #
    # Do not remove this without running `makemigrations --check` on Django
    # 6.0+ first: Translation.id has no explicit field declaration in
    # models.py (an explicit AutoField there was tried and reverted — it
    # doesn't carry the auto_created=True/serialize=False markers Django's
    # implicit PK generation sets, so it makes makemigrations detect a false
    # diff on every Django version, not just 6.0). This app-level pin is the
    # only thing keeping the implicit PK's type stable across Django
    # versions.
    default_auto_field = 'django.db.models.AutoField'
