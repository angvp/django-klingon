# History

## 0.1.0 (2026-07-04)

**Revival release** — modernized for current Django/Python.

* Added support for Django 4.2 LTS, 5.2 LTS, and 6.0; Python 3.10 through 3.14.
* Fixed several long-standing compatibility breakages: `ugettext` (removed in
  Django 4.0), `django.core.urlresolvers` (removed), `allow_tags` (ignored
  since Django 3.0 — the admin translations link was silently rendering as
  escaped text), `__unicode__` never called under Python 3.
* Pinned `default_auto_field` to `AutoField` so Django 6.0's new
  `BigAutoField` default doesn't force an unrequested PK migration on
  existing installs.
* Swapped the `django-autoslug` dependency for the maintained
  `django-easy-autoslug` fork.
* Migrated packaging from `setup.py` to `pyproject.toml`, replaced Travis CI
  with GitHub Actions, and switched linting from flake8 to ruff.
* Converted all documentation from reStructuredText to Markdown.

## 0.0.7 (2017-1-7)

* Removed support for Django 1.5 and 1.6 now klingon works from Django 1.7
  version in advance

## 0.0.4 (2015-1-2)

* Add translatable_slug and a painless integration with klingon +
  django-autoslug.
