dj_mano
=======

Materialized Annotations for Django Models. Typical use-case is to keep track of the number of
comments in a post, or the number of contributions a user has made.

Installation
------------

.. code-block:: bash

   pip install dj_mano

Usage
-----

.. code-block:: python

   @materialized_annotations
   class ModelA(models.Model):
       count_b = MaterializedAnnotationIntegerField(models.Count('models_b'))
       count_c = MaterializedAnnotationIntegerField(models.Count('models_b__models_c'))


   class ModelB(models.Model):
       model_a = models.ForeignKey('ModelA', related_name='models_b')


   class ModelC(models.Model):
       model_b = models.ForeignKey('ModelB', related_name='models_c')
