# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :

from django.test.testcases import TestCase
from django.db import models
from dj_mano.fields import MaterializedAnnotationIntegerField
from dj_mano.models import ModelA, ModelB, ModelC


class TestMaterializedAnnotationField(TestCase):
    def setUp(self):
        a1 = ModelA.objects.create()
        b1 = ModelB.objects.create(model_a=a1)
        b2 = ModelB.objects.create(model_a=a1)
        ModelC.objects.create(model_b=b1)
        ModelC.objects.create(model_b=b1)
        ModelC.objects.create(model_b=b2)

    def test_construct_class(self):
        f = MaterializedAnnotationIntegerField(42)
        self.assertIsInstance(f, models.IntegerField)
        self.assertEqual(42, f.annotation)

    def test_get_path(self):
        f = ModelA._meta.fields[2]
        path = f.get_path(ModelA)
        self.assertEqual(
            [ModelB._meta.fields[1], ModelC._meta.fields[1]],
            [x.join_field.field for x in path]
        )

    def test_list_lookups(self):
        f = ModelA._meta.fields[2]
        path = f.get_path(ModelA)
        lookups = list(f.list_lookups(path))

        self.assertEqual(
            [
                (ModelB, 'model_a'),
                (ModelC, 'model_b__model_a'),
            ],
            lookups
        )

    def test_compute(self):
        f = ModelA._meta.fields[2]
        f.compute(ModelA, [1])
        a = ModelA.objects.get(pk=1)
        self.assertEqual(3, a.count_c)

    def test_hooks(self):
        b1 = ModelB.objects.get(id=1)
        c4 = ModelC.objects.create(model_b=b1)
        c4.save()
        a1 = ModelA.objects.get(id=1)
        self.assertEqual(4, a1.count_c)
