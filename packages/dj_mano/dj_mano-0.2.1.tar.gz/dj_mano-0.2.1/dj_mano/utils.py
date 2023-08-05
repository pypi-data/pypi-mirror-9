# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :

from django.db import models
from .fields import MaterializedAnnotationField


def hook_it_all():
    # noinspection PyUnresolvedReferences
    for model in models.get_models():
        for field in model._meta.fields:
            if isinstance(field, MaterializedAnnotationField):
                field.hook_up(model)

