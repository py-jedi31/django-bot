from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig


class MyAdminSite(AdminSite):
    site_header = 'Бот "Марта"'
    site_title = 'Администрирование бота "Марта"'


admin_site_settings = MyAdminSite(name='myadmin')


class MyAdminConfig(AdminConfig):
    default_site = 'django_admin.web_service.admin_site.MyAdminSite'
