from django.contrib import admin
from django_admin.web_service.admin_site import admin_site_settings
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.translation import  gettext_lazy as _

from bot_marta.create_bot import bot_name
from django_admin.apps.useradmin.forms import CustomUserForm
from django_admin.apps.useradmin.models import CustomUser, Member, MemberState, CustomGroup


# @admin_site_settings.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'telegram_id', 'link_bot')}),
        (_('Permissions'), {
            'fields': ('groups', 'is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'on_vacation')}),
    )
    readonly_fields = ('link_bot',)

    list_display = ('username', 'first_name', 'last_name', 'email', 'telegram_id', 'on_vacation')
    form = CustomUserForm

    def link_bot(self, obj):
        if obj.username:
            return mark_safe(f'<a href="https://t.me/{bot_name}?start={obj.username}">Ссылка на бота</a>')
        return 'Для получения ссылки необходимо заполнить поле username'

    link_bot.short_description = "Бот"


# @admin_site_settings.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Пользователи"""
    list_display = ('name', 'tg_name', 'tg_id', 'region', 'unit', 'date')
    exclude = ('name', 'tg_name', 'tg_id', 'region', 'unit','date')

    def save_model(self, request, obj, form, change):
        return False


admin_site_settings.register(Member, MemberAdmin)
admin_site_settings.register(CustomGroup)
admin_site_settings.register(CustomUser, CustomUserAdmin)
# admin_site_settings.unregister(Group)
