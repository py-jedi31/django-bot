# Generated by Django 3.2.7 on 2021-10-27 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('poll', '0001_initial'),
        ('call_support', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberquestion',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='help_question', to='poll.member', verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='answeroperator',
            name='question',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='call_support.memberquestion', verbose_name='Вопрос'),
        ),
    ]