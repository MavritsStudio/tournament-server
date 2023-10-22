from django.contrib import admin

from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'status',
        'participant1',
        'participant2',
        'finish',
    )
    list_filter = ('status',)
