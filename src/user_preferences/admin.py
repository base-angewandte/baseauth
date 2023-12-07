from django.contrib import admin

from .models import (
    UserPreferencesData,
    UserSettings,
    UserSettingsApp,
    UserSettingsValue,
)


class UserPreferencesDataAdmin(admin.ModelAdmin):
    pass


class UserSettingsAppAdmin(admin.ModelAdmin):
    pass


class UserSettingsAdmin(admin.ModelAdmin):
    pass


class UserSettingsValueAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserPreferencesData, UserPreferencesDataAdmin)
admin.site.register(UserSettingsApp, UserSettingsAppAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(UserSettingsValue, UserSettingsValueAdmin)
