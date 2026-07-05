# django-klingon — Revival & Future Plan

> Working document. Captures the decisions and open questions from planning.
> Two parts: **Part 1 — Revival** (ship a modern release, low risk) and
> **Part 2 — Future** (the hybrid pluggable-backend idea, parked until Part 1 ships).

---

## Context & positioning

klingon does Django model translation via a **single generic-FK `Translation`
table** (`content_type`, `object_id`, `lang`, `field`, `translation`). Extend
`Translatable`, declare `translatable_fields`, and translations live as rows.

Three approaches in this space:

| | modeltranslation | **klingon** | django-nece |
|---|---|---|---|
| Storage | N real columns per field×lang | generic-FK rows, external table | 1 JSONB column on the model |
| Add field/language | schema migration | **no migration** | **no migration** |
| Filter by translated value | native SQL, indexable | ✗ weak (N lookups) | JSONB operators, GIN-indexable |
| DB portability | any backend | **any backend** | **PostgreSQL only** |
| Invasive to existing model | high | **none (external table)** | medium (data → JSONB) |
| Ecosystem / admin | huge | small | small |

**Honest positioning.** Don't pitch klingon as "better than modeltranslation"
in general — modeltranslation's column approach wins on admin/forms/DB
constraints/query ergonomics and has enormous ecosystem gravity (a former
workplace even migrated *off* nece *to* modeltranslation for these reasons).
klingon's real, narrow, defensible niche:

> **The zero-migration, database-agnostic, non-invasive way to add translations
> to models you can't or won't restructure — including on non-Postgres stacks
> where nece can't go.**

On Postgres, nece arguably occupies the "no-migration" niche *better* (same
flexibility + real query story). klingon's edge over nece is specifically
(1) DB-agnostic and (2) non-invasive (translations live entirely outside the
model table; `Translatable` is a pure behavior mixin).

---

## Part 1 — Revival (ship first)

**Target support window:** Django 4.2 LTS + 5.2 LTS + 6.0, Python 3.10–3.14.
Added 2026-07-04: Django 6.0 requires **Python ≥3.12** (3.10/3.11 dropped by
Django itself), so the matrix is not a full cross-product — see the tox/CI
exclusion below. Django 6.0 is a regular feature release (not LTS); no known
klingon-relevant removals beyond what Phase 1 already fixes — confirmed the
`format_html()` fix already passes `link` as an arg, so it's unaffected by
6.0's removal of bare no-arg `format_html()` calls.

**Found during execution (2026-07-04), not caught in planning:** Django 6.0
changed the global `DEFAULT_AUTO_FIELD` default from `AutoField` to
`BigAutoField`. Since klingon shipped without an `apps.py`/`AppConfig`
declaring its own `default_auto_field`, `makemigrations --check` on Django
6.0 wanted to alter `Translation.id` from `AutoField` to `BigAutoField` — an
unrequested PK-type migration that would hit every existing install. Fixed
by adding `klingon/apps.py` with `default_auto_field =
'django.db.models.AutoField'`, pinning the historical type. Verified clean
`makemigrations --check` and full suite pass on 4.2/5.2/6.0 after the fix.
**Total effort:** ~half a day to a shippable PyPI release.

### Phase 1 — compat + functional fixes (~2–3h)

Confirmed breakage (grepped, not guessed):

- `ugettext as _` → `gettext` — `klingon/models.py:11`, `klingon/admin.py:4`
  (removed Django 4.0)
- `django.core.urlresolvers` → `from django.urls import reverse` —
  `models.py:4,247` (the try/except's first branch is dead code)
- `translations_link.allow_tags = True` — `models.py:256`. Ignored since
  Django 3.0, so the admin link currently renders as **escaped text**
  (functional bug). Return `format_html(...)`, drop `allow_tags`.
- `__unicode__` → `__str__` — `models.py:41`, `tests/testapp/models.py`,
  `example_project/.../models.py`. `Translation` currently has no `__str__`.
- `USE_L10N` removed Django 5.0 → delete — `example_project/settings.py:78`
- Delete `klingon/compat.py` (Py2 `__future__` + Django 1.7–1.10 version
  shims); inline the two real imports (`GenericForeignKey`,
  `GenericTabularInline`).
- `MIDDLEWARE_CLASSES` → `MIDDLEWARE` (cosmetic, unused empty tuple).
- **Autoslug migration** — see below (folds into this phase).

#### Autoslug: swap to mireq's library

Move off `django-autoslug` / `django-autoslug-iplweb` to
**mireq's** (https://github.com/mireq/django-autoslugfield).

Confirmed facts:
- **PyPI install name is `django-easy-autoslug`** (v1.0.5) — *not*
  `django-autoslugfield` (that's just the repo/import name). Import stays
  `from django_autoslugfield import AutoSlugField`.
- `requires-python >=3.7`, depends on `django` **unpinned** → no version
  ceiling, works on Django 5.2. (This removes the old "autoslug compat is an
  external unknown" blocker.)
- Pure field library — no `apps.py`/`models.py`, so it does **not** need an
  `INSTALLED_APPS` entry.

API is **not** drop-in — three differences:
- `populate_from='name'` → `title_field='name'`
- field instance attr `.populate_from` → `.title_field` (default `None` →
  falls back to `str(instance)`)
- no exported slugify → use `from django.utils.text import slugify`

Exact edits:
- `klingon/models.py` L16–17: probe import → `from django_autoslugfield import
  AutoSlugField`; drop `from autoslug.settings import slugify`, use Django's
  unconditionally.
- `klingon/models.py` L222: `.populate_from` → `.title_field`. The existing
  `if auto_slug_obj:` guard (L226, initialized to `None` at L205) already
  handles the `None` case safely — a bare field just skips slug translation.
- `tests/testapp/models.py:7,26` + `example_project/testapp/models.py`:
  import path + `populate_from=` → `title_field=`.
- `tests/conftest.py:13`: remove `'autoslug'` from `INSTALLED_APPS`.
- `requirements-test.txt`: `django-autoslug-iplweb` → `django-easy-autoslug`.

Document in README: `title_field` is optional in the new lib (old
`populate_from` was mandatory). To use `translatable_slug` you **must** pass
`title_field='<field>'`; a bare `AutoSlugField()` silently skips per-language
slug translation (correct, non-crashing behavior).

### Phase 2 — packaging + CI (~2–3h)

- `setup.py` → `pyproject.toml` (PEP 621). Current classifiers falsely claim
  Py2.7/3.4 + Django 1.7/1.8. Kill the dead `setup.py sdist upload`.
  Single-source the version (today it's `__import__('klingon').__version__`).
- `tox.ini`: `{py27,py36,py37}-django{1.11,2.0,2.1}` → matrix below, with an
  **exclusion** since `django60` cannot run on py310/py311:
  ```
  [tox]
  envlist =
      {py310,py311,py312,py313,py314}-django{42,52}
      {py312,py313,py314}-django60

  [gh-actions]
  # mirrored as an explicit exclude: list in GH Actions matrix (below),
  # since tox envlist already encodes it via the separate second line.
  ```
- `.travis.yml` → GitHub Actions matrix, same py/django exclusion pairs
  (`django60` job only on `python-version: ['3.12','3.13','3.14']`).
- Add `makemigrations --check --dry-run` gate (migration `0001` already has
  `on_delete`, should apply clean) — run once per Django version, not once
  per matrix cell (redundant otherwise).

### Phase 3 — ship gate

If the suite passes on Django 5.2 + Py3.13 **and** Django 6.0 + Py3.13,
release to PyPI as-is. (5.2+3.13 stays the primary/fastest gate to check
first; 6.0 confirms the newer floor.)

### Deferred (separate decision, NOT part of the revival)

Bulk `annotate`/`prefetch` read helper to fix the per-field N-lookup weakness
(the `get_or_create` loop in `translate()`). This is the one investment that
neutralizes modeltranslation's query-ergonomics advantage, and it becomes the
`bulk_load` primitive in Part 2.

---

## Part 2 — Future: hybrid pluggable storage backend

**Status: parked behind Part 1. Do not start until the modern single-backend
release is green on CI.** Idea: choose storage strategy in settings so klingon
can be the external generic-FK table *or* use Postgres JSONB, behind one
generic API. Explicitly accepts that this "removes the easy part."

### Shape

Django-style pluggable backend:

```python
KLINGON_STORAGE_BACKEND = 'klingon.backends.RelationalBackend'
```

`Translatable` stops hitting the `Translation` table directly and delegates to
a backend implementing a small interface:

```python
class TranslationBackend:
    def get(self, obj, lang, field) -> str | None
    def set(self, obj, lang, field, text) -> None
    def get_all(self, obj, lang) -> dict           # {field: value}
    def delete(self, obj) -> None
    def bulk_load(self, queryset, lang) -> dict     # the deferred read helper
    supports_queryset_filtering: bool                # capability flag
```

Current generic-FK code becomes `RelationalBackend` and stays the **default**
(existing users untouched). Everything the mixin exposes today rewrites cleanly
on top of this.

### THE decision to make (sleep on this): B vs C

"Postgres → use JSONB" has two non-equivalent shapes:

- **B — external JSONB table.** One row *per object*:
  `(content_type, object_id, translations JSONB)`, GIN-indexed. A true drop-in
  backend (same interface, `obj` in / translations out). **Keeps klingon's
  identity** (model table untouched, non-invasive) and is a clean settings
  toggle. Gives JSONB *storage* but not native queryset filtering.

- **C — JSONB column on the model itself** (nece-style). This is where nece's
  killer feature lives: native `.language('de').filter(...)` at the queryset
  level, because the data is a real column on the real table.

**The crux:** the thing that makes JSONB *worth it* — native queryset filtering
— only comes from **C**. But **C cannot be a pure settings switch**: it needs a
field on the user's model, so the author must opt in structurally, which breaks
both "just flip a setting" and the non-invasive identity that is klingon's main
defensible ground. **B** preserves the identity but gives JSONB storage without
the superpower.

### Second constraint: generic API = lowest common denominator

A uniform API can only expose what all backends do (per-instance
get/set/translate). nece's `.language()` queryset filtering can't be part of
the uniform core because `RelationalBackend` can't do it efficiently. Honest
resolution: a **capability flag** — backends that can, expose a
`.translated(lang)` queryset method; backends that can't, raise a clear error.
"Compatible with both" therefore means "the common core is portable; the good
part is opt-in and backend-specific."

### Recommendation (for tomorrow's decision)

1. Ship Part 1 first. Part 2 is v2, not a prerequisite.
2. When building Part 2: implement the interface + `RelationalBackend` +
   `PostgresJSONBackend` **as shape B**. B is the coherent one — real settings
   toggle, preserves identity, GIN-indexed storage.
3. Add a management command to migrate data between backends (reuses the
   `translatemodels` infra) — a genuinely nice feature.
4. Treat **C** (on-model column + native queryset filtering) as a separate,
   explicitly-declared model option, **not** a global backend. It may not be
   worth building at all — it's largely re-implementing nece inside klingon.

### The real cost

Not the code — the **test matrix multiplying by backends**, and every future
feature having to work (or explicitly opt out) across all of them. For a
one-maintainer revival, go in with eyes open.

---

## Part 3 — Execution playbook (agents & models)

Decided 2026-07-04. Principle: the edits are pre-located and line-enumerated,
so the efficient shape is one main session for the interlocking code changes
plus two cheap parallel agents for the disjoint packaging/CI tracks — not a
multi-agent fan-out (four Phase-1 fixes touch `klingon/models.py`; splitting
them guarantees conflicts).

Model policy: **Fable is not needed anywhere in Part 1** — the discovery work
is already done and captured above. Run the main session on **Opus** (its two
judgment calls are small) and delegate everything mechanical to **Sonnet**
agents (`general-purpose` or the catch-all `claude` agent — either works).

Local env note: only Python 3.14 installed (Arch). Full 3.10–3.14 × Django
4.2/5.2/6.0 matrix (with the py310/py311 × django60 exclusion) is verified in
CI, not locally.

- **Wave 0 — baseline** (main session, Opus): branch `revival/part-1`, venv
  with Django 5.2, snapshot the failing suite (expect `ugettext` ImportError).
- **Wave 1 — parallel tracks**:
  - **A. Phase 1 compat + autoslug** — main session inline (Opus). All
    `klingon/*`, `tests/*`, `example_project/*`, `requirements-test.txt`
    edits + README `title_field` note. The only judgment calls
    (`format_html` admin link, `title_field=None` fallback) live here.
  - **B. Packaging** — general-purpose agent, **sonnet**, background.
    `setup.py` → PEP 621 `pyproject.toml`, single-source version, honest
    classifiers (Py 3.10–3.14, Django 4.2/5.2/6.0), `MANIFEST.in`.
  - **C. CI + tox** — general-purpose agent, **sonnet**, background.
    `tox.ini` per the Phase 2 matrix (`{py310–py314}-django{42,52}` +
    `{py312–py314}-django60`, django60 excluded on py310/py311), delete
    `.travis.yml`, GH Actions matrix with the matching `exclude:` block +
    `makemigrations --check --dry-run` gate.
  - **D. Trivial cleanup / dead-relic sweep** — general-purpose agent,
    **sonnet**, background. Purely mechanical, zero judgment calls, so it
    safely overlaps B and C:
    - Delete `.hgignore` (repo is git-only; Mercurial relic).
    - Delete `.travis.yml` (superseded by track C's GH Actions — coordinate
      so C doesn't also delete it; assign the actual deletion to whichever
      finishes first, D just flags/no-ops if already gone).
    - Grep-sweep for other dead references: `setup.py sdist upload` mentions
      in `CONTRIBUTING.rst`/`Makefile`, any leftover Py2 `__future__` imports
      outside `compat.py`, `MIDDLEWARE_CLASSES` mentions in docs, stale
      badge/shield URLs in `README.rst` (Travis badge → GH Actions badge,
      PyPI version badge if broken).
    - Report findings back rather than guessing on anything ambiguous (e.g.
      if a "dead" reference turns out to be load-bearing for docs builds).
  - File sets are disjoint → same working tree, no worktrees needed.
- **Wave 2 — integration** (main session, Opus): reconcile dep names across
  requirements/pyproject/tox (`django-easy-autoslug` everywhere), run suite on
  py3.14 + Django 5.2 first (primary gate), then py3.14 + Django 6.0
  (confirms the newer floor), migration check on both, fix fallout.
- **Wave 3 — ship gate**: user runs `/code-review` (medium); fix findings;
  push → CI proves the real matrix; green CI → propose commit/tag/PyPI steps
  (commit, tag, publish require explicit user approval).

No agent for: Part 2 (parked; future `Plan`/`angel-plan` design session),
the deferred bulk-read helper, or splitting Phase 1.

### Addendum — docs migrated to Markdown (2026-07-04, inline, main session)

Requested mid-execution, done after Wave 2. Converted every `.rst` in the
repo to `.md`: `README`, `HISTORY`, `AUTHORS`, `CONTRIBUTING` at the root, and
all of `docs/` (`index`, `installation`, `usage`, plus the `readme`/
`contributing`/`authors`/`history` include-stubs, now using MyST's
` ```{include} ` directive instead of RST's `.. include::`).

Follow-on changes required to keep this working, not just a rename:
- `docs/conf.py`: added `myst_parser` to `extensions`, changed `source_suffix`
  from `'.rst'` to `{'.md': 'markdown'}`. Added `docs/requirements.txt`
  (`sphinx`, `myst-parser`) since none existed before.
- `pyproject.toml`: dynamic `readme` file list updated to the `.md` files,
  **plus an explicit `content-type = "text/markdown"`** — without it,
  setuptools silently defaulted to `text/x-rst` even with `.md` source files
  (verified via a real `python -m build --sdist` + `PKG-INFO` inspection;
  this would have shipped a broken-rendering README to PyPI).
- `MANIFEST.in`: `.rst` → `.md` entries.
- Verified: `sphinx-build -b html docs/` succeeds, sdist contains the `.md`
  files with correct content-type, full test suite still 16/16 (docs-only
  change, no runtime code touched).

### Addendum — tooling parity with django-oml + Codecov + 0.1.0 (2026-07-04)

Requested mid-execution: copy best practices from the sibling `../django-oml`
repo (ruff, tox/CI style, packaging), switch coverage badge tooling to match,
and bump the version.

- **Ruff replaces flake8** everywhere: `pyproject.toml` gained `[tool.ruff]`
  (`target-version = "py310"`, `line-length = 88`) and `[tool.ruff.lint]`
  with `select = ["E", "W", "F", "I", "UP", "B", "C4", "DJ"]`, matching
  oml's config exactly. Added `[tool.ruff.lint.per-file-ignores]` exempting
  `*/migrations/*.py` from `E501` (generated code, standard Django
  convention). `runtests.py`'s `flake8_main` → `ruff_main`,
  `requirements-test.txt` and `Makefile`'s `lint` target updated.
  `Makefile` also had a pre-existing, unrelated bug fixed while in there:
  `lint`/`coverage`/`docs` targets referenced a literal `django-klingon`
  path instead of the actual `klingon` package dir.
  Also added `[dependency-groups] dev = [...]` for uv-based workflows,
  mirroring oml.
- **Brought the repo to a clean ruff baseline** rather than leaving new
  violations unaddressed (oml's own code is 100% clean under this config).
  34 findings fixed: import sorting, `super()` modernization, `u"..."` →
  plain strings, `%`-format → f-strings, `set([...])` → set literal in the
  migration, `raise ... from e` exception chaining, `ModelForm.exclude` →
  explicit `fields` tuple (verified the form still exposes the identical
  field set via a live instantiation check). One rule suppressed
  deliberately: `DJ001` (`TextField(null=True)`) on `Translation.translation`
  — changing this is a real schema migration affecting every existing
  install, out of scope for a lint cleanup; left as `# noqa: DJ001` with a
  comment explaining why. Re-verified full suite green on 4.2/5.2/6.0 after
  every mechanical rewrite (the `%`-format → f-string conversions in
  particular touch cache-key generation and the admin link, both covered
  indirectly by the test suite).
- **CI restructured to match oml's job split**: added a separate `lint` job
  (ruff on Python 3.12) ahead of the existing `test` matrix job, same
  pattern as oml's `ci.yml`.
- **Codecov replaces Coveralls**: `test` job now runs `coverage xml` after
  the suite and uploads via `codecov/codecov-action@v4` (gated to the
  Python 3.13 / Django 5.2 cell, oml's equivalent primary-cell gating
  pattern). `README.md` badges trimmed to two, matching oml's minimal set:
  GitHub Actions CI badge + Codecov coverage badge. Removed Coveralls,
  ReadTheDocs, and CodeClimate badges as deprecated/unmaintained for this
  project (no `.readthedocs.yaml` exists, so that badge was already
  pointing at a non-functional build).
- **Version bumped 0.0.7 → 0.1.0** in `klingon/__init__.py`, with a new
  `HISTORY.md` entry summarizing the whole revival. Classifier
  `Development Status` downgraded from the (inaccurate) `5 - Production/
  Stable` to `4 - Beta`, matching oml's convention for a 0.x release.
  Verified via a real `python -m build --sdist`: `PKG-INFO` shows
  `Version: 0.1.0`.
- **Not copied from oml** (judgment call, not asked): oml's
  `tests.py`-inside-package + `DJANGO_SETTINGS_MODULE`-based
  `[tool.pytest.ini_options]` pattern. klingon's tests live in a separate
  top-level `tests/` dir using `conftest.py`'s dynamic
  `settings.configure()` — a different, already-working structure: forcing
  it into oml's module-settings shape would be a bigger, riskier refactor
  than "tooling parity" calls for. Flagging here rather than silently
  skipping it.

### Addendum — code review fixes applied (2026-07-04)

Ran an 8-angle recall-biased `/code-review` against the full diff. No
correctness bugs survived verification (one candidate — a claimed
`IndentationError` in the CI `makemigrations-check` heredoc — looked serious
but was refuted by actually parsing the YAML and compiling the extracted
script: YAML's block-literal dedent strips the common indentation from every
line uniformly, so the heredoc terminator lands at column 0 correctly).
8 cleanup/maintainability findings survived and were applied:

- **Extracted `tests/settings.py`** (a plain `SETTINGS` dict) so
  `tests/conftest.py`'s `pytest_configure()` and the CI
  `makemigrations-check` job's heredoc both import the same source instead
  of hand-copying `INSTALLED_APPS`/`LANGUAGES` independently. Verified by
  actually running the refactored heredoc.
- **Cross-reference comments** added to `tox.ini` and
  `.github/workflows/tests.yml` pointing at each other's encoding of the
  "Django 6.0 needs Python ≥3.12" constraint (still two hand-maintained
  expressions of one fact — not eliminated, just harder to update one
  without noticing the other).
- **`pip install --no-deps -e .`** in the CI test job's install step, so a
  future narrowing of `pyproject.toml`'s `Django>=4.2,<7.0` range can't
  silently reinstall/upgrade Django out from under the matrix's exact
  per-cell pin.
- **`coverage xml` now only runs on the one matrix cell that uploads to
  Codecov** (python 3.13 / django 5.2), not all ~13 cells.
- **`[dependency-groups].dev` in `pyproject.toml` de-pinned** (bare
  `pytest`/`pytest-django`/`ruff` names, no versions) so
  `requirements-test.txt` stays the single versioned source of truth instead
  of two independently-drifting pin sets.
- **Two `self.translatable_fields = self.translatable_fields + (...)`
  spots** in `klingon/models.py` simplified to `+=`; the `view_name`
  intermediate variable in `translations_link` inlined.
- **Tried and reverted**: adding an explicit `id = models.AutoField(primary_key=True)`
  to `Translation` as defense-in-depth alongside `klingon/apps.py`'s
  `default_auto_field` pin. Verified this actually **breaks**
  `makemigrations --check` on every Django version (4.2/5.2/6.0), not just
  6.0 — an explicitly-declared field doesn't carry the
  `auto_created=True`/`serialize=False` markers Django's implicit PK
  generation sets, so the migration state permanently disagrees with the
  model state. Kept the `apps.py` pin as the only fix, with a long comment
  explaining why the model-level alternative doesn't work (so nobody
  re-attempts it).
- Re-verified full suite + `makemigrations --check` green on Django
  4.2/5.2/6.0 and a clean `ruff check` after every fix.

---

## Open questions to decide

- [ ] Go / no-go on the revival at all (Part 1).
- [ ] Part 2: build the hybrid backend, or keep klingon single-backend and lean
      purely on the DB-agnostic + non-invasive niche?
- [ ] If Part 2: **B or C** (see the crux above).
- [ ] Build the deferred bulk-read helper as part of Part 1, or hold it for
      Part 2 as `bulk_load`?
