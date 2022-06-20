from django.db.models import Q
from rest_framework import viewsets, permissions

from django_admin.apps.useradmin.models import Member, MemberState
from django_admin.apps.useradmin.serializers import MembersSerializer, MembersStateSerializer


class MembersViewSet(viewsets.ModelViewSet):
    """Пользователи бота."""
    model = Member
    serializer_class = MembersSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Member.objects.all()


class MembersStateViewSet(viewsets.ModelViewSet):
    """Пользователи бота."""
    model = MemberState
    serializer_class = MembersStateSerializer
    permission_classes = [permissions.AllowAny]
    queryset = MemberState.objects.all()

    def get_queryset(self):
        member_id = self.request.query_params.get('member', None)
        if member_id:
            queryset = self.queryset.filter(member=member_id)
            return queryset
        state = self.request.query_params.get('state', None)
        if state == 'main':
            queryset = self.queryset.filter(Q(state='BotState:MAIN')|Q(state='BotState:GAME')|Q(state='BotState:HELP'))
            return queryset
        return MemberState.objects.all()
