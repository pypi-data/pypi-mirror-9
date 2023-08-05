# coding=utf-8

from django.contrib import admin

from smsaero import models as _models


class MessageAdmin(admin.ModelAdmin):
    list_display = ('phone', 'text', 'identifier', 'status', 'created')
    search_fields = ('phone', 'text', 'identifier')
    list_filter = ('status',)
    fields = ('phone', 'text', 'identifier', 'status', 'created')
    readonly_fields = ('phone', 'text', 'identifier', 'status', 'created')


admin.site.register(_models.Message, MessageAdmin)
