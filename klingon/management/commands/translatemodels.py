from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<model_name model_name ...>'
    help = 'Create translation for specific models <app>.<model_name>'

    def handle(self, *args, **options):
        for model_name in args:
            try:
                pass
            except Exception as e:
                raise CommandError('Error, can not translate model "%s". %s' % (model_name, e))
            else:
                self.stdout.write('All translations created for "%s"' % model_name)