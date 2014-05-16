from django.contrib import admin
from klingon.models import Translation
from klingon.admin import TranslationInline, create_translations

from models import Book


class TranslationBookInline(TranslationInline):
    model = Translation


class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'translations_link')
    search_fields = ['title', 'description']
    list_filter = ['publication_date',]
    inlines = [TranslationBookInline]
    actions = [create_translations]

admin.site.register(Book, BookAdmin)
