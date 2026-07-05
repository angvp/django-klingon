import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError

from klingon.models import Translation


@pytest.mark.django_db
def test_translate_models_command_success(book):
    """Test translatemodels command creates translations for specified model."""
    call_command('translatemodels', 'testapp.Book')

    ifslug = 1 if book.translatable_slug else 0

    assert Translation.objects.count() == len(settings.LANGUAGES) * (
        len(book.translatable_fields) + ifslug
    )


@pytest.mark.django_db
def test_translate_models_command_empty():
    """Test translatemodels command with no arguments does nothing."""
    call_command('translatemodels')
    assert Translation.objects.count() == 0


@pytest.mark.django_db
def test_translate_models_command_wrong_args():
    """Test translatemodels command raises CommandError for invalid model."""
    with pytest.raises(CommandError):
        call_command('translatemodels', 'wrong.argument')


@pytest.mark.django_db
def test_translate_models_command_not_translatable_model():
    """Test translatemodels command raises CommandError for non-translatable model.

    ContentType always has rows in a test DB (created by Django's
    contenttypes machinery), so the command's loop actually runs and
    hits AttributeError when it calls .translate() on a plain model.
    """
    with pytest.raises(CommandError):
        call_command('translatemodels', 'contenttypes.ContentType')
