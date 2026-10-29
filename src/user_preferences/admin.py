from django.contrib import admin

from .models import (
    UserPreferencesData,
    UserSettings,
    UserSettingsApp,
    UserSettingsValue,
)


@admin.register(UserPreferencesData)
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


@admin.register(UserSettingsApp)
class UserSettingsAppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon')


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'app', 'title', 'value_type', 'default_value')


@admin.register(UserSettingsValue)
class UserSettingsValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'user_settings', 'user')
