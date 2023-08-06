# -*- coding: utf-8 -*-
from django.contrib import admin
from sanza.Users import models
from sanza.Users.forms import UserPreferencesAdminForm

class UserPreferencesAdmin(admin.ModelAdmin):
    form = UserPreferencesAdminForm
    list_display = ['user', 'notify_due_actions', 'message_in_favorites']
    #list_editable = ['notify_due_actions']
admin.site.register(models.UserPreferences, UserPreferencesAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "user", "content_type", "object_id"]
    list_filter  = ["user", "content_type"]
admin.site.register(models.Favorite, FavoriteAdmin)


class UserHomepageAdmin(admin.ModelAdmin):
    list_display = ["user", "url"]
admin.site.register(models.UserHomepage, UserHomepageAdmin)