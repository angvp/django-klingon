from django.core.management.base import BaseCommand, CommandError
from klingon.compat import get_model, V110, version
import os


class Command(BaseCommand):
    args = '<app.Model1 app.Model2 ...>'
    help = 'Create translation for specific models <app>.<model_name>' \
        ' \n Example: \n $ python manage.py translatemodels testapp.Book'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*', default=[])

    def handle(self, *args, **options):
        for model_name in args:
            try:
                app, name = model_name.split('.')
                model = get_model(app, name)
                for obj in model.objects.only('pk'):
                    obj.translate()
            except Exception as e:
                raise CommandError('Error, can not translate model "%s". %s' % (model_name, e))
            else:
                self.stdout.write('All translations created for "%s"' % model_name)
