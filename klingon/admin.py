from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from models import Translation


class TranslationAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'lang', 'field')
    search_fields = ('lang', 'field', 'translation')
    list_filter = ('lang', 'field', 'content_type')

admin.site.register(Translation, TranslationAdmin)


def create_translations(modeladmin, request, queryset):
    for obj in queryset:
        obj.translate()
create_translations.short_description = "Create translations for selected objects"


class TranslationInline(GenericTabularInline):
    extra = 0
    readonly_fields = ('lang', 'field')
    exclude = ('lang', 'field')
