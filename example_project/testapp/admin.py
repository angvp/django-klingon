from django.contrib import admin
from klingon.admin import TranslationInline, create_translations

from models import Book, Library

class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'translations_link')
    search_fields = ['title', 'description']
    list_filter = ['publication_date',]
    inlines = [TranslationInline]
    actions = [create_translations]

admin.site.register(Book, BookAdmin)


class LibraryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'translations_link')
    search_fields = ['name', 'description']
    inlines = [TranslationInline]
    actions = [create_translations]

admin.site.register(Library, LibraryAdmin)

