from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

get_model = apps.get_model


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
                raise CommandError(
                    f'Error, can not translate model "{model_name}". {e}'
                ) from e
            else:
                self.stdout.write(f'All translations created for "{model_name}"')
