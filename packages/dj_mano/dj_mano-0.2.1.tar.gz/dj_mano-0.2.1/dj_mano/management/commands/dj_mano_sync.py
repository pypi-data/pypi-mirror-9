# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :

from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import models
from dj_mano.fields import MaterializedAnnotationField


class Command(BaseCommand):
    help = 'Force re-calculation of all dj-mano based fields'

    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_true', dest='quiet', default=False),
    )

    def handle(self, quiet, *args, **options):
        # noinspection PyUnresolvedReferences
        for model in models.get_models():
            for field in model._meta.fields:
                if isinstance(field, MaterializedAnnotationField):
                    if not quiet:
                        self.stdout.write('---> {}.{}'.format(model._meta.db_table, field.name))
                    field.compute(model)
