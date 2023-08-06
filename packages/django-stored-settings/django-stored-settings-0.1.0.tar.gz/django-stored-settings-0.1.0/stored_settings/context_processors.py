# -*- coding: utf-8 -*-
from django.db.models.fields.files import ImageFieldFile
from django.db. models import ImageField
from stored_settings.models import Settings


def dynamic_settings(request):
    context = {}
    for setting in Settings.objects.all():
        if setting.type == 'box':
            setting.value = bool(setting.value)
        elif setting.type == 'image':
            setting.value = ImageFieldFile(instance=setting, field=ImageField(upload_to='settings'), name=setting.value)

        context[setting.key] = setting.value

    return {'dynamic_settings': context}