# Generated by Django 3.2.7 on 2022-01-25 11:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0014_auto_20211215_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата начала общения'),
            preserve_default=False,
        ),
    ]