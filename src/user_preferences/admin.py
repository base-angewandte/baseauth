from django.contrib import admin

from .models import (
    UserPreferencesData,
    UserSettings,
    UserSettingsApp,
    UserSettingsValue,
)


class UserPreferencesDataAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'showroom_id',
        'email',
        'affiliation',
        'organisational_unit',
        'complementary_email',
        'urls',
    )


class UserSettingsAppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon')


class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'app', 'title', 'value_type', 'default_value')


class UserSettingsValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'user_settings', 'user')


admin.site.register(UserPreferencesData, UserPreferencesDataAdmin)
admin.site.register(UserSettingsApp, UserSettingsAppAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(UserSettingsValue, UserSettingsValueAdmin)
