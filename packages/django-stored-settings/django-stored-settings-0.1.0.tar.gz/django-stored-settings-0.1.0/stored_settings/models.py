# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Settings(models.Model):
    class Type(object):
        CHAR = 'char'
        TEXT = 'text'
        HTML = 'text_html'
        BOOLEAN = 'boolean'
        IMAGE = 'image'

        DEFAULT = CHAR

        CHOICES = (
            (CHAR, _('One line input')),
            (BOOLEAN, _('Checkbox')),
            (IMAGE, _('Image Field')),
            (TEXT, _('Multi-line field')),
            (HTML, _('Multi-line field with HTML'))
        )
    name = models.CharField(_('Help text'), max_length=100)
    key = models.CharField(_('Field key'), max_length=100, unique=True)
    value = models.TextField(_('Value'), blank=True)
    type = models.CharField(_('Field type'), choices=Type.CHOICES, max_length=16, default=Type.DEFAULT)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.key)

    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Stored Settings')