"""
Test models used in django-klingon tests
"""
from django.db import models
from klingon.models import Translatable, AutomaticTranslation


class Book(models.Model, Translatable):
    title = models.CharField(max_length=100)
    description = models.TextField()
    publication_date = models.DateField()

    translatable_fields = ('title', 'description')

    def __unicode__(self):
        return self.title


class Library(AutomaticTranslation, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    translatable_fields = ('name', 'description')

    def __unicode__(self):
        return self.name
