# Generated by Django 3.2.7 on 2021-11-18 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0008_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='email address'),
        ),
    ]
