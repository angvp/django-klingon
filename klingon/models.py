from django.conf import settings
from django.core import urlresolvers
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models
from django.utils.translation import ugettext as _


class Translation(models.Model):
    """
    Model that stores all translations
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    lang = models.CharField(max_length=5, db_index=True)
    field = models.CharField(max_length=255, db_index=True)
    translation = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['lang', 'field']
        unique_together = (('content_type', 'object_id', 'lang', 'field'),)

    def __unicode__(self):
        return u'%s : %s : %s' % (self.content_object, self.lang, self.field)


class CanNotTranslate(Exception):
    pass


class Translatable(object):
    """
    Make your model extend this class to enable this API in you model instance
    instances.
    """
    translatable_fields = ()

    def translate(self):
        """
        Create all translations objects for this Translatable instance.

        @rtype: list of Translation objects
        @return: Returns a list of translations objects
        """
        translations = []
        for lang in settings.LANGUAGES:
            # do not create an translations for default language.
            # we will use the original model for this
            if lang[0] == self._get_default_language():
                continue
            # create translations for all fields of each language
            for field in self.translatable_fields:
                trans, created = Translation.objects.get_or_create(
                    object_id=self.id,
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
            object_id=self.id,
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
        key = self._get_translations_cache_key(lang)
        trans_dict = cache.get(key, {})
        if not trans_dict:
            for field in self.translatable_fields:
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
                    object_id=self.id,
                    content_type=ContentType.objects.get_for_model(self),
                    lang=lang,
                    field=field,
                )
        except Translation.DoesNotExist:
            if create:
                trans = Translation.objects.create(
                        object_id=self.id,
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
        # Read from cache
        key = self._get_translation_cache_key(lang, field)
        trans = cache.get(key, '')
        if not trans:
            trans_obj = self.get_translation_obj(lang, field)
            trans =  getattr(trans_obj, 'translation', '')
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
        if lang == self._get_default_language():
            raise CanNotTranslate(
                _('You are not supposed to translate the default language. '\
                'Use the model fields for translations in default language')
            )
        # Get translation, if it does not exits create one
        trans_obj = self.get_translation_obj(lang, field, create=True)
        trans_obj.translation = text
        trans_obj.save()
        # Update cache for this specif translations
        key = self._get_translation_cache_key(lang, field)
        cache.set(key, text)
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
        link = urlresolvers.reverse('admin:%s_%s_changelist' % (
            translation_type.app_label,
            translation_type.model),
        )
        object_type = ContentType.objects.get_for_model(self)
        link += '?content_type__id__exact=%s&object_id=%s' % (object_type.id, self.id)
        return '<a href="%s">translate</a>' % link
    translations_link.allow_tags = True
    translations_link.short_description = 'Translations'

    def _get_default_language(self):
        """
        Helper function to get defaul setting for klingon.
        This is not set at module level to make it easy to test
        """
        return getattr(settings, 'KLINGON_DEFAULT_LANGUAGE', '')

    def _get_translations_cache_key(self, lang):
        content_type = self._meta.object_name
        return '%s:%s:%s' % (content_type, self.id, lang)

    def _get_translation_cache_key(self, lang, field):
        content_type = self._meta.object_name
        return '%s:%s:%s:%s' % (content_type, self.id, lang, field)
