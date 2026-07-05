# django-klingon

[![Tests](https://github.com/angvp/django-klingon/actions/workflows/tests.yml/badge.svg)](https://github.com/angvp/django-klingon/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/angvp/django-klingon/branch/master/graph/badge.svg)](https://codecov.io/gh/angvp/django-klingon)

Welcome to the documentation for django-klingon!

django-klingon is an attempt to make django model translations suck
but with no integrations pain in your app!

## Setup & Integration

In your settings files:
add django-klingon to INSTALLED_APPS:

```python
INSTALLED_APPS = (
    ...
    'klingon',
    ...
)
```

specify a default language if you want to use your fields to store the
default language:

```python
KLINGON_DEFAULT_LANGUAGE = 'en'
```

Extend you models to add API support:
first add Translatable to your model Class definition. This will add the
API functions:

```python
from klingon.models import Translatable
...
class Book(models.Model, Translatable):
...
```

in the same model add an attribute to indicate which fields will be
translatables:

```python
    ...
    translatable_fields = ('title', 'description')
    ...
```

your model should look like this:

```python
class Book(models.Model, Translatable):
    title = models.CharField(max_length=100)
    description = models.TextField()
    publication_date = models.DateField()

    translatable_fields = ('title', 'description')
```

### Translating an autoslug field:

If you use [django-easy-autoslug](https://github.com/mireq/django-autoslugfield)'s
`AutoSlugField` and want the slug itself translated per-language, set
`translatable_slug` to the slug field's name **and** pass `title_field` to
the field so klingon knows which field to slugify from:

```python
from django_autoslugfield import AutoSlugField

class Book(models.Model, Translatable):
    title = models.CharField(max_length=100)
    slug = AutoSlugField(title_field='title')

    translatable_fields = ('title',)
    translatable_slug = 'slug'
```

`title_field` is optional in `django-easy-autoslug` (unlike the old
`django-autoslug`, where the equivalent `populate_from` was mandatory). A
bare `AutoSlugField()` with no `title_field` is valid and will not crash,
but klingon silently skips per-language slug translation for it.

### Add admin capabilities:

you can include an inline to your model admin and a custom action
to create the translations. To do this in your ModelAdmin class do
this:

```python
from klingon.admin import TranslationInline, create_translations
...
class BookAdmin(admin.ModelAdmin):
    ...
    inlines = [TranslationInline]
    actions = [create_translations]
```

* see full example in example_project folder of source code of klingon

### Using Specific Widgets in the TranslationInline form of the admin:

You can specify the widget to be use on an inline form by passing a dictionary to TranslationInlineForm.
So, you might want to extend the TranslationInline with a new form that will a "widgets" dictionary,
where you can specify the widget that each filds has to use, for example:

```python
class RichTranslationInlineForm(TranslationInlineForm):
    widgets = {
        'CharField': forms.TextInput(attrs={'class': 'klingon-char-field'}),
        'TextField': forms.Textarea(attrs={'class': 'klingon-text-field'}),
    }

class RichTranslationInline(TranslationInline):
    form = RichTranslationInlineForm
```

and then you just simply use the RichTranslationInline class on your AdminModels, for example:

```python
class BookAdmin(admin.ModelAdmin):
    inlines = [RichTranslationInline]
```

* see full example in example_project folder of source code of klingon

## Using the API

To create the translation you can do the follwing:

Suppose that you have and object called book:

```python
> book = Book.objects.create(
    title="The Raven",
    description="The Raven is a narrative poem",
    publication_date=datetime.date(1845, 1, 1)
)
```

you can create translation for that instances like this:

```python
> book.set_translation('es', 'title', 'El Cuervo')
> book.set_translation('es', 'description', 'El Cuervo es un poema narrativo')
```

a translation could be access individually:

```python
> self.book.get_translation('es', 'title')
'El Cuervo'
> book.get_translation('es', 'description')
'El Cuervo es un poema narrativo'
```

or you can get all translations together:

```python
> self.book.translations('es')
{
    'title': self.es_title,
    'description': self.es_description,
}
```

## Installation:

    pip install django-klingon

## Running the Tests

You can run the tests with via:

    python runtests.py

or:

    tox
