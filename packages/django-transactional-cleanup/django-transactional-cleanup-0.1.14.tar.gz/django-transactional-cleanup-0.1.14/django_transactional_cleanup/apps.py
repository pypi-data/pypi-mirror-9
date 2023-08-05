# coding: utf-8
import django
if django.VERSION >= (1, 7):

    from django.apps import AppConfig
    from .service import connect_signals

    class CleanupConfig(AppConfig):
        name = 'django_transactional_cleanup'

        def ready(self):
            connect_signals()
