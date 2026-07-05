import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('lang', models.CharField(max_length=5, db_index=True)),
                ('field', models.CharField(max_length=255, db_index=True)),
                ('translation', models.TextField(null=True, blank=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['lang', 'field'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='translation',
            unique_together={('content_type', 'object_id', 'lang', 'field')},
        ),
    ]
