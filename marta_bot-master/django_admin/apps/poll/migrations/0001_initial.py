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
                'verbose_name': 'ответ на опрос',
                'verbose_name_plural': 'ответы на опросы',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.PositiveIntegerField(verbose_name='Телеграм ID')),
                ('tg_name', models.CharField(max_length=32, verbose_name='Имя пользователя в Телеграм')),
                ('name', models.CharField(max_length=64, verbose_name='Имя')),
            ],
            options={
                'verbose_name': 'пользователя бота',
                'verbose_name_plural': 'пользователи бота',
                'db_table': 'members',
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'опрос',
                'verbose_name_plural': 'опросы',
                'db_table': 'polls',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст вопроса')),
                ('text_answer', models.BooleanField(verbose_name='Возможен ответ текстом?')),
                ('add_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
            ],
            options={
                'verbose_name': 'вопрос к опросу',
                'verbose_name_plural': 'вопросы',
                'ordering': ('add_date', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='QuestionOptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_key', models.PositiveSmallIntegerField(verbose_name='Количество кнопок')),
                ('text_key', models.CharField(help_text='Надписи кнопок записываются в строчку и разделяются ";"', max_length=256, verbose_name='Текст кнопок')),
            ],
            options={
                'verbose_name': 'кнопки ответов',
                'verbose_name_plural': 'кнопки ответов',
            },
        ),
        migrations.CreateModel(
            name='QuestionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=256, verbose_name='Ответ')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата ответа')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pquestion_answer', to='poll.member', verbose_name='Пользователь')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pquestion_answer', to='poll.question', verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'ответ к вопросу',
                'verbose_name_plural': 'ответы к вопросам',
            },
        ),
        migrations.AddField(
            model_name='question',
            name='options',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='poll.questionoptions', verbose_name='Варианты ответа'),
        ),
    ]
