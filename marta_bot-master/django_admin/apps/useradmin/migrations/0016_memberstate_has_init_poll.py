# Generated by Django 3.2.7 on 2022-01-26 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0015_member_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberstate',
            name='has_init_poll',
            field=models.BooleanField(default=False, verbose_name='Пройден стартовый опрос'),
        ),
    ]
