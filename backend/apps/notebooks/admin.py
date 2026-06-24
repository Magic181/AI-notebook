from django.contrib import admin

from .models import Notebook


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'is_favorite', 'updated_at')
    list_filter = ('is_favorite',)
    search_fields = ('name', 'description')
