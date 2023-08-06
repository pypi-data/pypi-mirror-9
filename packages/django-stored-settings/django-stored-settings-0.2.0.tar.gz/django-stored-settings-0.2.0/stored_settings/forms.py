# -*- coding: utf-8 -*-
import re
from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from stored_settings.models import Settings
from stored_settings.settings import ENABLE_TINYMCE, UPLOAD_TO_DIRECTORY

if ENABLE_TINYMCE:
    assert 'tinymce' in settings.INSTALLED_APPS
    from tinymce.widgets import TinyMCE as HtmlFieldWidget
else:
    HtmlFieldWidget = AdminTextareaWidget


class SettingsCreationForm(forms.ModelForm):
    class Meta:
        model = Settings

    def clean_key(self):
        data = self.cleaned_data['key']
        slug_re = re.compile(r'^[a-zA-Z0-9_]+$')

        if not slug_re.search(force_text(data)):
            raise ValidationError(_("Enter a valid 'key' consisting of letters, numbers or underscores."),
                                  code='invalid')
        return data


class SettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)

        if self.instance.type == Settings.Type.CHAR:
            self.fields['value'].widget = AdminTextInputWidget(attrs={})
        elif self.instance.type == Settings.Type.TEXT:
            self.fields['value'].widget = AdminTextareaWidget(attrs={'cols': 90, 'rows': 30},)
        elif self.instance.type == Settings.Type.HTML:
                self.fields['value'].widget = HtmlFieldWidget(attrs={'cols': 90, 'rows': 30},)
        elif self.instance.type == Settings.Type.IMAGE:
            new_field = ImageFieldFile(instance=self.instance, field=models.ImageField(upload_to=UPLOAD_TO_DIRECTORY),
                                       name=self.instance.value)
            self.fields['value'] = forms.ImageField(label=self.fields['value'].label, required=True)
            self.initial['value'] = new_field
        elif self.instance.type == Settings.Type.BOOLEAN:
            self.fields['value'].widget = forms.widgets.CheckboxInput(attrs={})
            self.fields['value'].label = 'Is true'

    def save(self, commit=True):
        instance = super(SettingsForm, self).save(commit=False)

        if self.instance.type == Settings.Type.BOOLEAN:
            # if it is checkbox and value is False - save as empty string
            if self.instance.value == 'False':
                self.instance.value = ''

        elif self.instance.type == Settings.Type.IMAGE and 'value' in self.changed_data:
            new_field = ImageFieldFile(instance=self.instance, field=models.ImageField(upload_to=UPLOAD_TO_DIRECTORY),
                                       name=self.instance.value.name)
            new_field.field.name = 'value'
            new_field.save(self.instance.value.name, self.instance.value, True)
            self.instance.value = self.instance.value.lower()

        if commit:
            instance.save()
        return instance