from django.apps import AppConfig


class UserPreferencesConfig(AppConfig):
    name = 'user_preferences'

    def ready(self):
        # import signal handlers
        from . import signals  # noqa: F401
