# Generated by Django 3.2.7 on 2021-12-23 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0014_auto_20211215_1409'),
        ('poll', '0005_alter_questionanswer_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('member', 'poll')},
        ),
    ]
