klingon
========================


.. image:: https://coveralls.io/repos/angvp/django-klingon/badge.png?branch=master
  :target: https://coveralls.io/r/angvp/django-klingon?branch=master

.. image:: https://travis-ci.org/angvp/django-klingon.svg?branch=master
  :target: http://travis-ci.org/angvp/django-klingon

.. image:: https://readthedocs.org/projects/django-klingon/badge/?version=latest
  :target: https://readthedocs.org/projects/django-klingon/?badge=latest
  :alt: Documentation Status

Welcome to the documentation for django-klingon!

django-klingon is an attempt to make django model translations suck
but with no integrations pain in your app!

Setup & Integration
------------------------------------

In your settings files:
add django-klingon to INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'klingon',
        ...
    )

specify a default language if you want to use your fields to store the
default language::

    KLINGON_DEFAULT_LANGUAGE = 'en'

Extend you models to add API support:
first add Translatable to your model Class definition. This will add the
API functions::

    from klingon.models import Translatable
    ...
    class Book(models.Model, Translatable):
    ...

in the same model add an attribute to indicate which fields will be
translatables::

        ...
        translatable_fields = ('title', 'description')
        ...

your model should look like this::

    class Book(models.Model, Translatable):
        title = models.CharField(max_length=100)
        description = models.TextField()
        publication_date = models.DateField()

        translatable_fields = ('title', 'description')


Add admin capabilities:
______________________

you can include an inline to your model admin and a custom action
to create the translations. To do this in your ModelAdmin class do
this::

    from klingon.admin import TranslationInline, create_translations
    ...
    class BookAdmin(admin.ModelAdmin):
        ...
        inlines = [TranslationInline]
        actions = [create_translations]

* see full example in example_project folder of source code of klingon


Using Specific Widgets in the TranslationInline form of the admin:
________________________________________________

You can specify the widget to be use on an inline form by passing a dictionary to TranslationInlineForm.
So, you might want to extend the TranslationInline with a new form that will a "widgets" dictionary, 
where you can specify the widget that each filds has to use, for example::

    class RichTranslationInlineForm(TranslationInlineForm):
        widgets = {
            'CharField': forms.TextInput(attrs={'class': 'klingon-char-field'}),
            'TextField': forms.Textarea(attrs={'class': 'klingon-text-field'}),
        }

    class RichTranslationInline(TranslationInline):
        form = RichTranslationInlineForm

and then you just simply use the RichTranslationInline class on your AdminModels, for example::

    class BookAdmin(admin.ModelAdmin):
        inlines = [RichTranslationInline]

* see full example in example_project folder of source code of klingon

Using the API
------------------------------------

To create the translation you can do the follwing:

Suppose that you have and object called book::

    > book = Book.objects.create(
        title="The Raven",
        description="The Raven is a narrative poem",
        publication_date=datetime.date(1845, 1, 1)
    )

you can create translation for that instances like this::

    > book.set_translation('es', 'title', 'El Cuervo')
    > book.set_translation('es', 'description', 'El Cuervo es un poema narrativo')

a translation could be access individually::

    > self.book.get_translation('es', 'title')
    'El Cuervo'
    > book.get_translation('es', 'description')
    'El Cuervo es un poema narrativo'

or you can get all translations together::

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


.. image:: https://d2weczhvl823v0.cloudfront.net/RouteAtlas/django-klingon/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

