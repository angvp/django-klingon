from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext as _

INSTALLED_AUTOSLUG = False

try:
    from django_autoslugfield import AutoSlugField  # noqa: F401

    INSTALLED_AUTOSLUG = True
except ImportError:  # pragma: no cover - dep is always present in the suite
    pass


class Translation(models.Model):
    """
    Model that stores all translations
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    lang = models.CharField(max_length=5, db_index=True)
    field = models.CharField(max_length=255, db_index=True)
    # null=True predates this ruff rule and is part of the shipped schema;
    # changing it would require an ALTER COLUMN migration for every install.
    translation = models.TextField(blank=True, null=True)  # noqa: DJ001

    class Meta:
        ordering = ['lang', 'field']
        unique_together = (('content_type', 'object_id', 'lang', 'field'),)

    def __str__(self):
        return f'{self.content_object} : {self.lang} : {self.field}'


class CanNotTranslate(Exception):
    pass


class Translatable:
    """
    Make your model extend this class to enable this API in you model instance
    instances.
    """
    translatable_fields = ()
    translatable_slug = None

    def _all_translatable_fields(self):
        """
        translatable_fields plus the translatable_slug (if declared and not
        already listed). Computed instead of mutating translatable_fields,
        so class and instance state never diverge.
        """
        fields = tuple(self.translatable_fields)
        if self.translatable_slug is not None \
                and self.translatable_slug not in fields:
            fields += (self.translatable_slug,)
        return fields

    def translate(self):
        """
        Create all translations objects for this Translatable instance.

        @rtype: list of Translation objects
        @return: Returns a list of translations objects
        """
        self._assert_saved()
        translations = []
        for lang in settings.LANGUAGES:
            # do not create an translations for default language.
            # we will use the original model for this
            if lang[0] == self._get_default_language():
                continue
            # create translations for all fields of each language
            for field in self._all_translatable_fields():
                trans, created = Translation.objects.get_or_create(
                    object_id=self.pk,
                    content_type=ContentType.objects.get_for_model(self),
                    field=field,
                    lang=lang[0],
                )
                translations.append(trans)

        return translations

    def translations_objects(self, lang):
        """
        Return the complete list of translation objects of a Translatable
        instance

        @type lang: string
        @param lang: a string with the name of the language

        @rtype: list of Translation
        @return: Returns a list of translations objects
        """
        return Translation.objects.filter(
            object_id=self.pk,
            content_type=ContentType.objects.get_for_model(self),
            lang=lang
        )

    def translations(self, lang):
        """
        Return the list of translation strings of a Translatable
        instance in a dictionary form

        @type lang: string
        @param lang: a string with the name of the language

        @rtype: python Dictionary
        @return: Returns a all fieldname / translations (key / value)
        """
        if self.pk is None:
            return {
                field: self.get_translation(lang, field)
                for field in self._all_translatable_fields()
            }

        key = self._get_translations_cache_key(lang)
        trans_dict = cache.get(key, {})

        if not trans_dict:
            for field in self._all_translatable_fields():
                # we use get_translation method to be sure that it will
                # fall back and get the default value if needed
                trans_dict[field] = self.get_translation(lang, field)

            cache.set(key, trans_dict)
        return trans_dict

    def get_translation_obj(self, lang, field, create=False):
        """
        Return the translation object of an specific field in a Translatable
        istance

        @type lang: string
        @param lang: a string with the name of the language

        @type field: string
        @param field: a string with the name that we try to get

        @rtype: Translation
        @return: Returns a translation object
        """
        trans = None
        try:
            trans = Translation.objects.get(
                object_id=self.pk,
                content_type=ContentType.objects.get_for_model(self),
                lang=lang,
                field=field,
            )
        except Translation.DoesNotExist:
            if create:
                self._assert_saved()
                trans = Translation.objects.create(
                    object_id=self.pk,
                    content_type=ContentType.objects.get_for_model(self),
                    lang=lang,
                    field=field,
                )
        return trans

    def get_translation(self, lang, field):
        """
        Return the translation string of an specific field in a Translatable
        istance

        @type lang: string
        @param lang: a string with the name of the language

        @type field: string
        @param field: a string with the name that we try to get

        @rtype: string
        @return: Returns a translation string
        """
        if self.pk is None:
            return getattr(self, field, '')

        # Read from cache
        key = self._get_translation_cache_key(lang, field)
        trans = cache.get(key, '')

        if not trans:
            trans_obj = self.get_translation_obj(lang, field)
            trans = getattr(trans_obj, 'translation', '')
            # if there's no translation text fall back to the model field
            if not trans:
                trans = getattr(self, field, '')
            # update cache
            cache.set(key, trans)
        return trans

    def set_translation(self, lang, field, text):
        """
        Store a translation string in the specified field for a Translatable
        istance

        @type lang: string
        @param lang: a string with the name of the language

        @type field: string
        @param field: a string with the name that we try to get

        @type text: string
        @param text: a string to be stored as translation of the field
        """
        # Do not allow user to set a translations in the default language
        auto_slug_obj = None

        if lang == self._get_default_language():
            raise CanNotTranslate(
                _('You are not supposed to translate the default language. '
                  'Use the model fields for translations in default language')
            )

        self._assert_saved()

        # Get translation, if it does not exits create one
        trans_obj = self.get_translation_obj(lang, field, create=True)
        trans_obj.translation = text
        trans_obj.save()

        # Update cache for this specific translation
        key = self._get_translation_cache_key(lang, field)
        cache.set(key, text)

        # check if the field has an autoslugfield and, if the field just
        # translated is the slug's *source* field, regenerate the slug
        # translation from it. An explicit translation of the slug field
        # itself is never overwritten, because only the source field
        # triggers regeneration.
        if INSTALLED_AUTOSLUG and self.translatable_slug:
            try:
                slug_field = self._meta.get_field(self.translatable_slug)
                auto_slug_obj = slug_field.title_field
            except AttributeError:
                pass

        if auto_slug_obj and field == auto_slug_obj:
            tobj = self.get_translation_obj(lang, self.translatable_slug, create=True)
            translation = self.get_translation(lang, auto_slug_obj)
            tobj.translation = slugify(translation)
            tobj.save()
            # keep the slug's per-field cache in sync with the new value
            slug_key = self._get_translation_cache_key(lang, self.translatable_slug)
            cache.set(slug_key, tobj.translation)

        # remove cache for translations dict
        cache.delete(self._get_translations_cache_key(lang))
        return trans_obj

    def translations_link(self):
        """
        Print on admin change list the link to see all translations for this object

        @type text: string
        @param text: a string with the html to link to the translations admin interface
        """
        translation_type = ContentType.objects.get_for_model(Translation)
        link = reverse(
            f'admin:{translation_type.app_label}_{translation_type.model}_changelist'
        )

        object_type = ContentType.objects.get_for_model(self)
        link += f'?content_type__id__exact={object_type.id}&object_id={self.pk}'
        return format_html('<a href="{}">translate</a>', link)

    translations_link.short_description = 'Translations'

    def _get_default_language(self):
        """
        Helper function to get defaul setting for klingon.
        This is not set at module level to make it easy to test
        """
        return getattr(settings, 'KLINGON_DEFAULT_LANGUAGE', '')

    def _assert_saved(self):
        """
        Raise CanNotTranslate if this instance has not been saved yet;
        translations are linked to the object's primary key.
        """
        if self.pk is None:
            raise CanNotTranslate(
                _('Save the instance before creating translations: '
                  'translations are linked to the object primary key')
            )

    def _get_translations_cache_key(self, lang):
        # label_lower is app-qualified, so equally-named models in
        # different apps can not collide on cache keys
        return f'{self._meta.label_lower}:{self.pk}:{lang}'

    def _get_translation_cache_key(self, lang, field):
        return f'{self._get_translations_cache_key(lang)}:{field}'


class AutomaticTranslation(Translatable):
    """
    Model that automatically crates translations
    """

    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)
        self.translate()
        return res
