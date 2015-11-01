"""
Test models used in django-klingon tests
"""
from django.db import models
from klingon.models import Translatable, AutomaticTranslation

from autoslug import AutoSlugField


class Book(models.Model, Translatable):
    title = models.CharField(max_length=100)
    description = models.TextField()
    publication_date = models.DateField()
    slug = models.SlugField()

    translatable_fields = ('title', 'description')
    translatable_slug = 'slug'

    def __unicode__(self):
        return self.title


class Library(AutomaticTranslation, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = AutoSlugField(populate_from='name')

    translatable_fields = ('name', 'description')
    translatable_slug = 'slug'

    def __unicode__(self):
        return self.name
