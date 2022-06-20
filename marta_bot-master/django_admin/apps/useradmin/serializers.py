from rest_framework import serializers

from django_admin.apps.useradmin.models import Member, MemberState


class MembersSerializer(serializers.ModelSerializer):
    """Пользователи."""
    class Meta:
        model = Member
        fields = (
            'tg_id',
            'tg_name',
            'name'
        )


class MembersStateSerializer(serializers.ModelSerializer):
    """Пользователи."""
    class Meta:
        model = MemberState
        fields = (
            'member',
            'main_message_id',
            'pin_message_id',
            'state',
        )
