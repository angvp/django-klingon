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
* Fixed a stale-cache bug: translating the slug's source field (e.g. `name`)
  regenerated the slug translation row but left the old value in the
  per-field cache, so `get_translation()` kept returning the stale slug.
* Fixed explicit slug translations being silently overwritten: calling
  `set_translation()` on the slug field itself no longer triggers auto-slug
  regeneration — the explicitly-set value now wins.
* Translation cache keys are now app-qualified (`app_label.model` instead of
  the bare class name), so identically-named models in different apps can no
  longer collide. Existing cache entries are invalidated once on upgrade.
* `translate()` and `set_translation()` on an unsaved instance now raise
  `CanNotTranslate` with a clear message instead of a database
  `IntegrityError`.
* `translate()`/`translations()` no longer mutate `translatable_fields` to
  append the `translatable_slug`; the combined list is computed internally.
* `Translatable` now uses `pk` instead of assuming an `id` attribute, so
  models with a custom-named integer primary key work.

## 0.0.7 (2017-1-7)

* Removed support for Django 1.5 and 1.6 now klingon works from Django 1.7
  version in advance

## 0.0.4 (2015-1-2)

* Add translatable_slug and a painless integration with klingon +
  django-autoslug.
