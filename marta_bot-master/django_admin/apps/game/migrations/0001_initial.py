# Generated by Django 3.2.7 on 2021-10-27 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата ответа')),
            ],
            options={
                'verbose_name': 'ответ на вопрос',
                'verbose_name_plural': 'ответы на вопросы',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст вопроса')),
                ('add_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('picture', models.ImageField(blank=True, default=None, max_length=1024, null=True, upload_to='django_admin/static/game_picture/%Y/%m/%d', verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'вопрос к интерактиву',
                'verbose_name_plural': 'вопросы к интерактиву',
                'ordering': ('add_date',),
            },
        ),
        migrations.CreateModel(
            name='QuestionOptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=64, verbose_name='Текст варианта')),
                ('true_answer', models.BooleanField(verbose_name='Верный ответ?')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='option', to='game.question', verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'варианты ответов',
                'verbose_name_plural': 'варианты ответов',
            },
        ),
    ]
