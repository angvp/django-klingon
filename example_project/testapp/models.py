"""
Test models used in django-klingon tests
"""
from django.db import models
from klingon.models import Translatable, AutomaticTranslation


class Book(models.Model, Translatable):
    title = models.CharField(max_length=100)
    description = models.TextField()
    publication_date = models.DateField()
    slug = models.SlugField()

    translatable_fields = ('title', 'description', 'slug')
    translatable_slug = 'slug'

    def __str__(self):
        return self.title


class Library(AutomaticTranslation, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    translatable_fields = ('name', 'description')

    def __str__(self):
        return self.name
