from django import forms
from django.contrib import admin
from klingon.admin import TranslationInline, TranslationInlineForm, create_translations

from models import Book, Library

class RichTranslationInlineForm(TranslationInlineForm):
    widgets = {
        'CharField': forms.TextInput(attrs={'class': 'klingon-char-field'}),
        'TextField': forms.Textarea(attrs={'class': 'klingon-text-field'}),
    }

class RichTranslationInline(TranslationInline):
    form = RichTranslationInlineForm


class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'translations_link')
    search_fields = ['title', 'description']
    list_filter = ['publication_date',]
    inlines = [RichTranslationInline]
    actions = [create_translations]

admin.site.register(Book, BookAdmin)


class LibraryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'translations_link')
    search_fields = ['name', 'description']
    inlines = [TranslationInline]
    actions = [create_translations]

admin.site.register(Library, LibraryAdmin)

