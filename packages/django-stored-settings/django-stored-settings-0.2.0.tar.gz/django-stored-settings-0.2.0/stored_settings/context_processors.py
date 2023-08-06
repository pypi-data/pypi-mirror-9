# -*- coding: utf-8 -*-
from django.db.models.fields.files import ImageFieldFile
from django.db. models import ImageField
from stored_settings.models import Settings
from stored_settings.settings import UPLOAD_TO_DIRECTORY


def stored_settings(request):
    context = {}
    for setting in Settings.objects.all():
        if setting.type == Settings.Type.BOOLEAN:
            setting.value = bool(setting.value) and 1 or 0
        elif setting.type == Settings.Type.IMAGE:
            setting.value = ImageFieldFile(instance=setting, field=ImageField(upload_to=UPLOAD_TO_DIRECTORY),
                                           name=setting.value)

        context[setting.key] = setting.value

    return {'stored_settings': context}