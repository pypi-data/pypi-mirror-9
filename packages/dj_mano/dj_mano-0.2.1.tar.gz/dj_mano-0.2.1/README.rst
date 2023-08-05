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

In-code
~~~~~~~

Using dj_mano is pretty straightforward, you just create a field and give it the annotation you
want it to hold.

If you want, you can apply some filter to the annotation you're doing, like to count only positive
reviews by example. In this case, you can provide a function that will return the queryset that
will be annotated. Beware, the queryset must be "starting" from the object holding the materialized
annotation field.

Models
......

.. code-block:: python

   from django.db import models
   from dj_mano import MaterializedAnnotationIntegerField


   def swag_model_c():
       return ModelA.objects.filter(models_b__models_c__has_swag=True)


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


urls.py
.......

.. code-block:: python

   from django.conf.urls import patterns
   from dj_mano import hook_it_all

   hook_it_all()

   urlpatterns = patterns('',
       ...
   )

Command
~~~~~~~

There is a command that will simply synchronize all fields to their actual value.

**Note**: if you want to use this command, you have to put `dj_mano` in your `INSTALLED_APPS`.

.. code-block:: bash

   ./manage.py dj_mano_sync

Licence
-------

This library is licensed under the terms of the WTFPL. Please see the attached LICENSE file.
