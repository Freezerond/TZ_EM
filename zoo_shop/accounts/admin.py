from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'name', 'surname', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('name', 'patronymic', 'surname',)}),
        ('Права доступа', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Даты', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'patronymic', 'surname', 'password1', 'password2', 'role', 'is_active')}
        ),
    )

admin.site.register(User, UserAdmin)