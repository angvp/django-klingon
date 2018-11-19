from __future__ import (division, print_function, unicode_literals,
                        with_statement)

from django import VERSION
from django.apps.registry import apps
from django.contrib.contenttypes.admin import GenericTabularInline

from django.contrib.contenttypes.fields import GenericForeignKey

version = VERSION[1]

V17 = 7
V18 = 8
V19 = 9
V110 = 10

get_model = apps.get_model

__all__ = ['get_model', 'GenericForeignKey', 'GenericTabularInline']
