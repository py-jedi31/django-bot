# Generated by Django 3.2.7 on 2021-10-27 18:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('game', '0001_initial'),
        ('poll', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='owner',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='game_question', to=settings.AUTH_USER_MODEL, verbose_name='Создатель'),
        ),
        migrations.AddField(
            model_name='answer',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gquestion_answer', to='poll.member', verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='answer',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='game.questionoptions', verbose_name='Ответ'),
        ),
    ]
