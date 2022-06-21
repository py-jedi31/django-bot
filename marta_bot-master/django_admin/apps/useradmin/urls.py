"""
v1/ - urls для добавления пользователей
"""

from django.urls import include, path

from django_admin.apps.useradmin.router import router_v1

urlpatterns = [
    path(
        'v1/',
        include(router_v1.urls)
    ),
]
