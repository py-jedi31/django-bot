# Generated by Django 3.2.7 on 2022-01-31 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0016_memberstate_has_init_poll'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberstate',
            name='has_init_poll',
            field=models.BooleanField(default=False, null=True, verbose_name='Пройден стартовый опрос'),
        ),
    ]