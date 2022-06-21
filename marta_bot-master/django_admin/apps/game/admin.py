"""
Регистрация моделей в админке
"""


from django.contrib import admin
from django_admin.web_service.admin_site import admin_site_settings
from django.utils.safestring import mark_safe

from django_admin.apps.game.models import Question, QuestionOptions


class QuestionOptionsAdmin(admin.TabularInline):
    """Варианты ответов на вопросы"""
    model = QuestionOptions


# @admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Вопросы"""
    list_display = ('text', 'add_date', 'update_date', 'owner', 'ispicture', 'is_active','has_true_answer')
    inlines = (QuestionOptionsAdmin, )
    readonly_fields = ('get_picture', )
    exclude = ('owner', 'cash')
    empty_value_display = 'Пользователь удален'
    ordering = ('-is_active', 'add_date',)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.cash = None
        super().save_model(request, obj, form, change)

    @admin.display(boolean=True, description="Изображение")
    def ispicture(self, obj):
        if obj.picture:
            return True
        return False

    @admin.display(boolean=True, description="Один верный ответ?")
    def has_true_answer(self, obj):
        n = 0
        for option in obj.option.all():
            if option.true_answer:
                n += 1
        if n == 1:
            return True
        return False

    def get_picture(self, obj):
        if obj.picture:
            return mark_safe(f'<img src="{obj.picture.url}" style="max-width:600px;width:100%">')
        return ''

    get_picture.short_description = "Превью"


admin_site_settings.register(Question, QuestionAdmin)
