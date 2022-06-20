# Generated by Django 3.2.7 on 2021-11-18 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call_support', '0009_auto_20211117_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answeroperator',
            name='text',
            field=models.TextField(help_text='Максимальное количество символов в ответе 3500', max_length=1900, null=True, verbose_name='Ответ'),
        ),
        migrations.AlterField(
            model_name='memberquestion',
            name='text',
            field=models.TextField(max_length=1900, verbose_name='Вопрос'),
        ),
    ]