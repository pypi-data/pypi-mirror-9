import django

from .service import connect_signals

if django.VERSION < (1, 7):
    connect_signals()
