# coding=utf-8

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _


class Message(models.Model):
    phone = models.CharField(verbose_name=_(u'phone number'), max_length=12)
    text = models.TextField(verbose_name=_(u'text'))
    status = models.CharField(verbose_name=_(u'status'), max_length=128, blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u'created'), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u'modified'), auto_now=True)

    class Meta:
        verbose_name = _(u'message')
        verbose_name_plural = _(u'messages')

    def __unicode__(self):
        return ugettext(u'Message to {0} on {1}').format(self.phone, self.created)
