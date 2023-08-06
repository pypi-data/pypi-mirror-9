# -*- coding: utf-8 -*-
"""
Model admins for Django admin
"""
from django.contrib import admin
from models import *

class EntityAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_filter = ('created', 'modified', 'kind')
    list_display = ('name', 'kind', 'created', 'modified')

class NoteAdmin(admin.ModelAdmin):
    list_filter = ('created', 'modified', 'author')
    list_display = ('title', 'entity', 'author', 'created', 'modified')
    raw_id_fields = ('entity', 'author')

admin.site.register(Entity, EntityAdmin)
admin.site.register(Note, NoteAdmin)
