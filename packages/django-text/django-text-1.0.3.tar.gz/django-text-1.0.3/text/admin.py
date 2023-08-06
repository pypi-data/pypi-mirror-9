from django.contrib import admin
from django.db import models

from .models import Text
from .widgets import MarkdownEditorWidget


class TextAdmin(admin.ModelAdmin):
    list_display = ('name', )
    formfield_overrides = {
        models.TextField: {'widget': MarkdownEditorWidget},
    }


admin.site.register(Text, TextAdmin)
