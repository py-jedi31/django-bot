# Generated by Django 3.2.7 on 2021-12-03 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0012_customgroup'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customgroup',
            options={'verbose_name': 'группу прав доступа', 'verbose_name_plural': 'группы прав доступа'},
        ),
    ]
