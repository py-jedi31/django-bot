# Generated by Django 3.2.7 on 2021-11-02 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call_support', '0004_alter_memberquestion_member'),
    ]

    operations = [
        migrations.CreateModel(
            name='PinMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Для отображения ссылок в сообщении воспользуйтесь конструкцией (текст)[ссылка]', verbose_name='Текст сообщения')),
            ],
            options={
                'verbose_name': 'Закрепленное сообщение',
                'verbose_name_plural': 'Закрепленное сообщение',
            },
        ),
    ]