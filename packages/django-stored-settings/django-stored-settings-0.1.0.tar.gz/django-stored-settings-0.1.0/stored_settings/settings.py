from django.conf import settings

ENABLE_TINYMCE = getattr(settings, 'STORED_SETTINGS_TINYMCE_ENABLE', False)

UPLOAD_TO_DIRECTORY = getattr(settings, 'STORED_SETTINGS_UPLOAD_TO', 'stored-settings')