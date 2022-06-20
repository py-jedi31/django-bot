from django.contrib.auth import get_user_model
from django.core.validators import validate_image_file_extension, FileExtensionValidator
from django.db import models

from django_admin.apps.poll.models import Member


class Question(models.Model):
    """Вопросы для интерактива."""

    text = models.TextField("Текст вопроса", max_length=4096)
    add_date = models.DateTimeField("Дата создания", auto_now_add=True)
    update_date = models.DateTimeField("Дата изменения", auto_now=True)
    picture = models.ImageField(
        "Изображение",
        upload_to="game_picture/%Y/%m/%d",
        null=True,
        blank=True,
        default=None,
        max_length=1024,
        validators=(FileExtensionValidator(['jpg', 'jpeg', 'png']),)
    )
    cash = models.CharField("Кэш фото", max_length=128, null=True)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Создатель",
        default=1,
        related_name="game_question",
    )
    is_active = models.BooleanField('Активный', default=True)

    class Meta:
        verbose_name = "вопрос к интерактиву"
        verbose_name_plural = "вопросы к интерактиву"
        ordering = ("add_date",)

    def __str__(self):
        return self.text


class QuestionOptions(models.Model):
    """Варианты ответа для вопроса"""

    text = models.CharField("Текст варианта", max_length=64)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name="Вопрос", related_name="option"
    )
    true_answer = models.BooleanField("Верный ответ?")

    class Meta:
        verbose_name = "варианты ответов"
        verbose_name_plural = "варианты ответов"

    def __str__(self):
        return self.text + f"({self.question.pk})"


class Answer(models.Model):
    """Ответы пользователей на вопросы интерактива"""

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="gquestion_answer",
    )
    option = models.ForeignKey(
        QuestionOptions, on_delete=models.CASCADE, verbose_name="Ответ"
    )
    date = models.DateTimeField("Дата ответа", auto_now_add=True)

    class Meta:
        verbose_name = "ответ на вопрос"
        verbose_name_plural = "ответы на вопросы"

    def __str__(self):
        return f"""Вопрос:{self.option.question.pk},
                   пользователь: {self.member.name}, 
                   дата: {self.date.strftime('%d.%m.%y %H:%M')}"""
