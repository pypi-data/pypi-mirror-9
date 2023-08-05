# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :

from django.db import models
from dj_mano.fields import MaterializedAnnotationIntegerField, materialized_annotations


def swag_model_c():
    return ModelA.objects.filter(models_b__models_c__has_swag=True)


@materialized_annotations
class ModelA(models.Model):
    count_b = MaterializedAnnotationIntegerField(models.Count('models_b'))
    count_c = MaterializedAnnotationIntegerField(models.Count('models_b__models_c'))
    count_swag = MaterializedAnnotationIntegerField(
        models.Count('models_b__models_c'),
        swag_model_c
    )


class ModelB(models.Model):
    model_a = models.ForeignKey('ModelA', related_name='models_b')


class ModelC(models.Model):
    model_b = models.ForeignKey('ModelB', related_name='models_c')
    has_swag = models.BooleanField(default=False)
