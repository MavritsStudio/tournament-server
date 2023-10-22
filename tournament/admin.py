from django.contrib import admin

from .models import Tournament, Round


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'status',
        'organizer',
    )
    list_filter = ('status',)
    raw_id_fields = ('teams',)
    search_fields = ('name',)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "description", 'organizer', 'contact', 'limit'),
            },
        ),
    )