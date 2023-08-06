# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import SessionInfo


# noinspection PyUnusedLocal
def invalidate_sessions(modeladmin, request, queryset):
    for session in queryset:
        session.erase()

invalidate_sessions.short_description = _("Log out users")


class SessionInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'creation_date', 'key', 'active', 'prefix')
    list_filter = ('creation_date', 'prefix', 'active')
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'creation_date', 'key', 'prefix', 'session_exists', 'session_exists_db', 'session_data']
    actions = [invalidate_sessions, ]

    def save_model(self, request, obj, form, change):
        if 'active' in form.changed_data and not obj.active:
            obj.erase()
        # model is read-only except of active

admin.site.register(SessionInfo, SessionInfoAdmin)