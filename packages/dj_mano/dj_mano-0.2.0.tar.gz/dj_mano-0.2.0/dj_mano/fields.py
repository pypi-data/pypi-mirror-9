# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.db.models.signals import post_save, post_delete
from django.utils.six import with_metaclass


# noinspection PyArgumentList,PyUnresolvedReferences
class MaterializedAnnotationField(object):
    description = 'A field that keeps an up-to-date annotation materialized in the model'

    def __init__(self, annotation, queryset=None, *args, **kwargs):
        """
        Annotation is an argument you would give to QuerySet's annotate() function, and the result
        of this annotation will be automatically be saved and kept up to date in this field.

        In some cases you might want to do some filtering in your calculations. You can do so by
        providing a callable in queryset that will return the base queryset from which the
        annotation will be done. The idea is the following:

            queryset().annotate(annotation)

        :param annotation:
        :param queryset:
        :param args:
        :param kwargs:
        :return:
        """

        super(MaterializedAnnotationField, self).__init__(*args, **kwargs)
        self.annotation = annotation
        self.queryset = queryset
        self.hooked = False

    def get_queryset(self, model):
        if self.queryset is None:
            return model.objects.all()
        else:
            return self.queryset()

    # noinspection PyMethodMayBeStatic
    def process_value(self, value):
        return value

    def compute(self, model, ids=None):
        """
        Computes and update the field value in the model instances for the given ids.

        Update is done in SQL directly, so the instances are not fetched. The downside is that the
        ORM is not aware of the changes.

        :param model:
        :param ids:
        :return:
        """
        name = '{}_calc'.format(self.name)
        qs = self.get_queryset(model).annotate(**{name: self.annotation})

        if ids is not None:
            qs = qs.filter(pk__in=ids)

        values = qs.values_list('pk', self.name, name)

        for pk, current, value in values:
            value = self.process_value(value)
            if current != value:
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
            post_delete.connect(self.on_post_save(lookup), sender=model, weak=False)

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

    def get_db_prep_value(self, value, connection, prepared=False):
        # noinspection PyUnresolvedReferences
        value = super(MaterializedAnnotationField, self) \
            .get_db_prep_value(value, connection, prepared)
        return self.process_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super(MaterializedAnnotationField, self).deconstruct()
        kwargs['annotation'] = True
        return name, path, args, kwargs

    def south_field_triple(self):
        from south.modelsinspector import introspector

        args, kwargs = introspector(self)
        kwargs.update({
            'annotation': True,
        })

        return (
            '{}.{}'.format(self.__class__.__module__, self.__class__.__name__),
            args,
            kwargs,
        )


class MaterializedAnnotationNumberField(MaterializedAnnotationField):
    def __init__(self, annotation, queryset=None, null_to_zero=True, *args, **kwargs):
        """
        Base class for Integer/Float fields.

        :param null_to_zero: when saving, if value is None convert it to 0
        :return:
        """
        kwargs['default'] = 0
        self.null_to_zero = null_to_zero
        super(MaterializedAnnotationNumberField, self).__init__(
            annotation,
            queryset,
            *args,
            **kwargs
        )

    def process_value(self, value):
        if self.null_to_zero and value is None:
            return 0

        return value


class MaterializedAnnotationIntegerField(with_metaclass(models.SubfieldBase,
                                                        MaterializedAnnotationNumberField,
                                                        models.IntegerField)):
    pass


class MaterializedAnnotationFloatField(with_metaclass(models.SubfieldBase,
                                                      MaterializedAnnotationNumberField,
                                                      models.FloatField)):
    pass
