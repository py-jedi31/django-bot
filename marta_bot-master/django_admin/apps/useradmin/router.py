from rest_framework.routers import DefaultRouter

from django_admin.apps.useradmin.views import MembersViewSet, MembersStateViewSet

router_v1 = DefaultRouter()

router_v1.register(
    'members',
    MembersViewSet,
    basename='members'
)

router_v1.register(
    'member_state',
    MembersStateViewSet,
    basename='member_state'
)
