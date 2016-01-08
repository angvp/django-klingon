from __future__ import print_function, unicode_literals, with_statement, division
from django import VERSION


V18 = VERSION[1] == 8
V19 = VERSION[1] == 9

if V18:
    from django.db.models.loading import get_model
    from django.contrib.contenttypes.generic import GenericForeignKey
    from django.contrib.contenttypes.generic import GenericTabularInline
elif V19:
    from django.apps.registry import apps
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.admin import GenericTabularInline

    get_model = apps.get_model


__all__ = ['get_model', 'GenericForeignKey', 'GenericTabularInline']
