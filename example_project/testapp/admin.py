from django.contrib import admin
from klingon.admin import TranslationInline, create_translations

from models import Book

class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'translations_link')
    search_fields = ['title', 'description']
    list_filter = ['publication_date',]
    inlines = [TranslationInline]
    actions = [create_translations]

admin.site.register(Book, BookAdmin)
