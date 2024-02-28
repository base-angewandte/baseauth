from django.conf import settings as django_settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _

from user_preferences.models import UserSettings, UserSettingsApp


class Command(BaseCommand):
    help = 'Create UserSettingsApp and UserSettings instances.'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            nargs='+',
            type=str,
            help=_('A name for your app.'),
        ),

    def handle(self, *args, **options):
        # Make app
        if 'app_name' not in options:
            raise CommandError('Please specify at least one app name.')

        options_app_name = options['app_name'][0].lower()

        if options_app_name not in django_settings.SETTINGS_DATA:
            raise CommandError(
                'App with name {} is not yet configured'.format(options['app_name'][0])
            )

        app, created = UserSettingsApp.objects.get_or_create(
            id=options_app_name,
            name=django_settings.SETTINGS_DATA[options_app_name]['title'],
        )
        app.icon = django_settings.SETTINGS_DATA[app.id].get('icon')
        app.save()

        # Make settings
        for setting_id, setting in django_settings.SETTINGS_DATA[app.id][
            'settings'
        ].items():
            user_settings, created = UserSettings.objects.get_or_create(
                id=setting_id, app=app
            )
            user_settings.title = setting['title']
            user_settings.value_type = setting['type']
            user_settings.default_value = setting['default_value']
            user_settings.save()

        self.stdout.write(self.style.SUCCESS('Successfully created app and settings'))
