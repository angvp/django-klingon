from __future__ import print_function, unicode_literals, with_statement, division
from django import VERSION

version = VERSION[1]

V15 = 5
V16 = 6
V17 = 7
V18 = 8
V19 = 9


if version in [V15, V16]:
    from django.db.models.loading import get_model
    from django.contrib.contenttypes.generic import GenericForeignKey, GenericTabularInline

if version in [V17, V18, V19]:
    from django.apps.registry import apps
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.admin import GenericTabularInline
    get_model = apps.get_model


__all__ = ['get_model', 'GenericForeignKey', 'GenericTabularInline']
