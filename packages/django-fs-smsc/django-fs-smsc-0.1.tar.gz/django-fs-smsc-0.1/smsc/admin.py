# coding=utf-8

from django.contrib import admin

from smsc import models as _models


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'text', 'status', 'created', 'modified')
    search_fields = ('id', 'phone', 'text')
    list_filter = ('status',)
    fields = ('id', 'phone', 'text', 'status', 'created', 'modified')
    readonly_fields = ('id', 'phone', 'text', 'status', 'created', 'modified')


admin.site.register(_models.Message, MessageAdmin)
