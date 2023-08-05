import logging

from django.db import models, connection
from django.db.utils import DEFAULT_DB_ALIAS, ConnectionHandler
from django.db.models.signals import pre_save, post_delete

from transaction_hooks.mixin import TransactionHooksDatabaseWrapperMixin

logger = logging.getLogger(__name__)


def _find_models_with_filefield():
    result = []
    for model in models.get_models():
        for field in model._meta.fields:
            if isinstance(field, models.FileField):
                result.append(model)
                break
    return result


def _delete_file(file_obj):
    def delete_from_storage():
        try:
            storage.delete(file_obj.name)
        except Exception:
            logger.exception("Unexpected exception while attempting to delete old file '%s'" % file_obj.name)

    storage = file_obj.storage
    if storage and storage.exists(file_obj.name):
        connection.on_commit(delete_from_storage)


def _get_file_fields(instance):
    return filter(
        lambda field: isinstance(field, models.FileField),
        instance._meta.fields,
    )


def remove_files_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except instance.DoesNotExist:
        return

    for field in _get_file_fields(instance):
        old_file = getattr(old_instance, field.name)
        new_file = getattr(instance, field.name)

        if old_file and old_file != new_file:
            _delete_file(old_file)


def remove_files_on_delete(sender, instance, **kwargs):
    for field in _get_file_fields(instance):
        file_to_delete = getattr(instance, field.name)

        if file_to_delete:
            _delete_file(file_to_delete)


def connect_signals():
    connections = ConnectionHandler()
    backend = connections[DEFAULT_DB_ALIAS]
    if isinstance(backend, TransactionHooksDatabaseWrapperMixin):
        for model in _find_models_with_filefield():
            pre_save.connect(remove_files_on_change, sender=model)
            post_delete.connect(remove_files_on_delete, sender=model)
        return

    logger.warn("WARNING: Using backend without django-transaction-hooks support, auto delete files will not work.")
