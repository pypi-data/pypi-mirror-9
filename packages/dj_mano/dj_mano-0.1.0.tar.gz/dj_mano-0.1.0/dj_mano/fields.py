# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.backends.signals import connection_created
from django.db.models.constants import LOOKUP_SEP
from django.db.models.signals import post_save
from django.utils.six import with_metaclass


def materialized_annotations(cls):
    """
    Class decorator to initialize materialized annotations in the specified model.
    """

    def do(**kwargs):
        connection_created.disconnect(do, weak=False)
        for field in cls._meta.fields:
            if isinstance(field, MaterializedAnnotationField):
                field.hook_up(cls)

    connection_created.connect(do, weak=False)

    return cls


# noinspection PyArgumentList,PyUnresolvedReferences
class MaterializedAnnotationField(object):
    description = 'A field that keeps an up-to-date annotation materialized in the model'

    def __init__(self, annotation, *args, **kwargs):
        super(MaterializedAnnotationField, self).__init__(*args, **kwargs)
        self.annotation = annotation
        self.hooked = False

    def get_queryset(self, model):
        return model.objects.all()

    def compute(self, model, ids):
        """
        Computes and update the field value in the model instances for the given ids.

        Update is done in SQL directly, so the instances are not fetched. The downside is that the
        ORM is not aware of the changes.

        :param model:
        :param ids:
        :return:
        """
        name = '{}_calc'.format(self.name)
        values = self.get_queryset(model)\
            .filter(pk__in=ids)\
            .annotate(**{name: self.annotation})\
            .values_list('pk', name)

        for pk, value in values:
            model.objects.filter(pk=pk).update(**{self.name: value})

    def on_post_save(self, lookup):
        def do(instance, **kwargs):
            try:
                fields = lookup.split(LOOKUP_SEP)

                ptr = instance
                for field in fields:
                    ptr = getattr(ptr, field)

                    if ptr is None:
                        break

                if ptr is not None:
                    self.compute(ptr.__class__, [ptr.pk])
            except ObjectDoesNotExist:
                pass
        return do

    def hook_up(self, model):
        if self.hooked:
            return

        self.hooked = True

        path = self.get_path(model)
        for model, lookup in self.list_lookups(path):
            post_save.connect(self.on_post_save(lookup), sender=model, weak=False)

    def get_path(self, model):
        """
        Computes the join path of a query with this annotation starting from the given model.

        :param model: models.Model
        :return:
        """
        q = self.get_queryset(model).query

        field_list = self.annotation.lookup.split(LOOKUP_SEP)
        opts = model._meta

        field, sources, opts, join_list, path = q.setup_joins(
            field_list,
            opts,
            q.get_initial_alias(),
        )

        return path

    def list_lookups(self, path):
        """
        For a given path (computed by get_path()), give all the reverse lookups that the field need
        to listen to in order to detect changes.
        :param path:
        :return:
        """

        chain = [x.join_field.field for x in path]

        for i in range(0, len(chain)):
            model = chain[i].model
            fields = []
            for field in reversed(chain[0:i + 1]):
                fields.append(field.name)

            yield model, LOOKUP_SEP.join(fields)

    def deconstruct(self):
        name, path, args, kwargs = super(MaterializedAnnotationField, self).deconstruct()
        kwargs['annotation'] = True
        return name, path, args, kwargs


class MaterializedAnnotationIntegerField(with_metaclass(models.SubfieldBase,
                                                        MaterializedAnnotationField,
                                                        models.IntegerField)):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = 0
        super(MaterializedAnnotationIntegerField, self).__init__(*args, **kwargs)
