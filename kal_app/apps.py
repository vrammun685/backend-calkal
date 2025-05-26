from django.apps import AppConfig
import sys
import os

class KalAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kal_app'

    def ready(self):
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') == 'true':
            from . import script
            script.start_in_background()

