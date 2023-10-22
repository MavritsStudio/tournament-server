from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Team


@admin.register(get_user_model())
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", 'middle_name')}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    list_display = (
        'uid',
        'email',
        'first_name',
        'last_name',
        'is_staff',
    )
    list_filter = (
        'is_staff',
        'is_active',
    )
    search_fields = tuple()
    ordering = None


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("name", "mate1", 'mate2', 'description')}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "mate1", 'mate2', 'description'),
            },
        ),
    )

    list_display = (
        'code',
        'name',
        'mate1',
        'mate2',
        'created',
    )
    search_fields = ('name',)
