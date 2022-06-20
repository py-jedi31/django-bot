import threading
from django_admin.web_service.admin_site import admin_site_settings
from django.contrib import admin
from django.utils.safestring import mark_safe

from bot_marta.utils import answer_support, edit_pin_message, send_newsletter
from django_admin.apps.call_support.models import AnswerOperator, PinMessage, Newsletter
from django_admin.apps.useradmin.models import MemberState


# @admin.register(AnswerOperator)
class MemberQuestionAdmin(admin.ModelAdmin):
    """Вопросы"""
    list_display = ('question_title', 'member_name', 'answer_title', 'date_create', 'date_update', "user", "is_answer")
    exclude = ('user', 'question')
    empty_value_display = '-----'
    ordering = ('-user', '-date_create', )
    list_filter = ('user',)

    @admin.display(description='Ответ')
    def answer_title(self, obj):
        text = obj.text
        if text:

            if len(text) > 30:
                return f'{obj.text[:30]}...'
        return obj.text

    @admin.display(description='Вопрос')
    def question_title(self, obj):
        text = obj.question.text
        if len(text) > 30:
            return f'{obj.question.text[:30]}...'
        return obj.question.text

    @admin.display(description='Пользователь')
    def member_name(self, obj):
        return obj.question.member.name

    @admin.display(description='Дата ответа')
    def date_answer(self, obj):
        if not obj.text:
            return '-----'
        return obj.date_update

    @admin.display(description='Отвечено', boolean=True)
    def is_answer(self, obj):
        if obj.text:
            return True
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        t1 = threading.Thread(target=answer_support(obj))
        super().save_model(request, obj, form, change)
        t1.start()
        t1.join()


@admin.register(PinMessage)
class PinMessageAdmin(admin.ModelAdmin):
    """Закрепленное сообщение"""
    def save_model(self, request, obj, form, change):
        user_list = MemberState.objects.all()
        super().save_model(request, obj, form, change)
        t1 = threading.Thread(target=edit_pin_message(user_list, obj.text))
        t1.start()
        t1.join()


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Вопросы"""
    list_display = ('text', 'date_create', "owner", 'ispicture')
    exclude = ('owner', 'cash',)
    readonly_fields = ('get_picture',)
    empty_value_display = '-=Пусто=-'
    ordering = ('-date_create', )

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.cash = None
        super().save_model(request, obj, form, change)
        user_list = MemberState.objects.all()
        t1 = threading.Thread(target=send_newsletter(user_list, obj.text, obj.picture))
        t1.start()
        t1.join()

    @admin.display(description="Изображение", boolean=True)
    def ispicture(self, obj):
        if obj.picture:
            return True
        return False

    @admin.display(description="Превью")
    def get_picture(self, obj):
        if obj.picture:
            return mark_safe(f'<img src="{obj.picture.url}" style="max-width:600px;width:100%">')
        return '-'


admin_site_settings.register(AnswerOperator, MemberQuestionAdmin)
admin_site_settings.register(PinMessage, PinMessageAdmin)
admin_site_settings.register(Newsletter, NewsletterAdmin)
