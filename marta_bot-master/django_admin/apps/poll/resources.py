from import_export import resources
from import_export import  fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from django_admin.apps.poll.models import Poll, Answer
from django_admin.apps.useradmin.models import Member


class PollAnswerResource(resources.ModelResource):
    """Форма для создания таблиц импорта/экспорта расписания"""
    member_name = fields.Field(column_name='Имя пользователя', attribute='member', widget=ForeignKeyWidget(Member, 'name'))
    member_region = fields.Field(column_name='Регион', attribute='member', widget=ForeignKeyWidget(Member, 'region'))
    member_unit = fields.Field(column_name='Департамент', attribute='member', widget=ForeignKeyWidget(Member, 'unit'))
    poll = fields.Field(column_name='Опрос', attribute='poll', widget=ForeignKeyWidget(Poll, 'title'))
    question_answer = fields.Field(column_name='Ответы')
    # class_room = fields.Field(column_name='Номер ауд.', attribute='class_room',)
    # lesson = fields.Field(column_name='Номер урока', attribute='lesson',widget=ForeignKeyWidget(NumberLesson, 'pk'))
    date = fields.Field(column_name='Дата', attribute='date',)

    class Meta:
        model = Answer
        exclude = ('id', 'member')

    def dehydrate_question_answer(self,  obj):
        questions = "".join([f'{q.question.text} - {q.answer}\n' for q in obj.member.pquestion_answer.filter(question__poll=obj.poll).order_by('pk')])
        return questions
