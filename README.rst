klingon
========================

Welcome to the documentation for django-klingon!

django-klingon is an attempt to make django model translations suck
but with no integrations pain in your app!

Setup & Integration
------------------------------------

In your settings files:
add django-klingon to INSTALLED_APPS:

```
    INSTALLED_APPS = (
        ...
        'klingon',
        ...
    )
```

specify a default language if you want to use your fields to store the
default language:

    KLINGON_DEFAULT_LANGUAGE = 'en'

Extend you models to add API support:
first add Translatable to your model Class definition. This will add the
API functions

```
    from klingon.models import Translatable
    ...
    class Book(models.Model, Translatable):
    ...
```

in the same model add an attribute to indicate which fields will be
translatables:

        ...
        translatable_fields = ('title', 'description')
        ...

your model should look like this:

    class Book(models.Model, Translatable):
        title = models.CharField(max_length=100)
        description = models.TextField()
        publication_date = models.DateField()

        translatable_fields = ('title', 'description')


Add admin capabilities:
you can include an inline to your model admin and a custom action
to create the translations. To do this in your ModelAdmin class do
this:

    from klingon.admin import TranslationInline, create_translations
    ...
    class BookAdmin(admin.ModelAdmin):
        ...
        inlines = [TranslationInline]
        actions = [create_translations]

* see full example in example_project folder of source code of klingon


Using the API
------------------------------------

To create the translation you can do the follwing:

Suppose that you have and object called book:

    > book = Book.objects.create(
        title="The Raven",
        description="The Raven is a narrative poem",
        publication_date=datetime.date(1845, 1, 1)
    )

you can create translation for that instances like this

    > book.set_translation('es', 'title', 'El Cuervo')
    > book.set_translation('es', 'description', 'El Cuervo es un poema narrativo')

a translation could be access individually:

    > self.book.get_translation('es', 'title')
    'El Cuervo'
    > book.get_translation('es', 'description')
    'El Cuervo es un poema narrativo'

or you can get all translations together:

    > self.book.translations('es')
    {
        'title': self.es_title,
        'description': self.es_description,
    }

Installation:
------------------------------------

    pip install django-klingon


Running the Tests
------------------------------------

You can run the tests with via::

    python setup.py test

or::

    python runtests.py
