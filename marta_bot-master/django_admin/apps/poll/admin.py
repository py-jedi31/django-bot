from django.contrib import admin
from django_admin.web_service.admin_site import admin_site_settings
from django.utils.safestring import mark_safe
from import_export.admin import ExportActionMixin

from .forms import QuestionForm
from .models import Poll, Question, QuestionOptions,  Answer
from .resources import PollAnswerResource


class InlineQuestionAdmin(admin.TabularInline):
    """Варианты ответов на вопросы"""
    model = Question
    # readonly_fields = ('owner', )
    extra = 0
    exclude = ('owner', )
    form = QuestionForm


# @admin_site_settings.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """Опросы"""
    list_display = ('title',)
    inlines = (InlineQuestionAdmin, )
    ordering = ('id',)


# @admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Вопросы"""
    list_display = ('text', 'text_answer', 'poll', 'options', 'add_date', 'update_date', 'owner')
    exclude = ('owner',)
    list_filter = ('poll',)
    empty_value_display = 'Пользователь удален'

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


# @admin.register(QuestionOptions)
class QuestionOptionsAdmin(admin.ModelAdmin):
    """Варианты ответов на вопросы"""
    list_display = ('text_key', 'count_key',)
    exclude = ('count_key',)

    def save_model(self, request, obj, form, change):
        obj.count_key = len(request.POST.get('text_key').split(";"))
        super().save_model(request, obj, form, change)


# @admin.register(Answer)
class QuestionAnswerAdmin(ExportActionMixin, admin.ModelAdmin):
    """Ответы пользователей на опрос"""
    resource_class = PollAnswerResource
    list_display = ('member_name', 'member_region', 'member_unit', 'poll', 'question_answer', 'date')
    readonly_fields = ('question_answer', 'member_name', 'member_region', 'member_unit')
    list_filter = ('poll', 'member__region', 'member__unit', 'date')
    list_display_links = None
    search_fields = ('member__name', 'member__region', 'member__unit')

    @admin.display(description='Ответы')
    def question_answer(self,  obj):
        questions = "".join([f'{q.question.text} - {q.answer}<br>'
                             for q in obj.member.pquestion_answer.filter(
                                                                         question__poll=obj.poll,
                                                                         date=obj.date
                                                                        ).order_by('pk')])
        return mark_safe(questions)

    @admin.display(description='Имя пользователя')
    def member_name(self, obj):
        return obj.member.name

    @admin.display(description='Регион')
    def member_region(self, obj):
        return obj.member.region

    @admin.display(description='Департамент')
    def member_unit(self, obj):
        return obj.member.unit


admin_site_settings.register(Poll, PollAdmin)
admin_site_settings.register(QuestionOptions, QuestionOptionsAdmin)
admin_site_settings.register(Answer, QuestionAnswerAdmin)
