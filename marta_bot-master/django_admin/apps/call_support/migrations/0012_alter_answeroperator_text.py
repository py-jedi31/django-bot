# Generated by Django 3.2.7 on 2021-12-15 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call_support', '0011_alter_answeroperator_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answeroperator',
            name='text',
            field=models.TextField(help_text='Максимальное количество символов в ответе 1900 \n                                       | Для отображения ссылок в сообщении воспользуйтесь конструкцией \n                                       [текст](ссылка)', max_length=1900, null=True, verbose_name='Ответ'),
        ),
    ]