# Generated by Django 3.2.7 on 2021-12-23 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('useradmin', '0014_auto_20211215_1409'),
        ('poll', '0004_alter_question_text'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='questionanswer',
            unique_together={('member', 'question')},
        ),
    ]
