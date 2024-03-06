from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from user_preferences.models import UserPreferencesData, UserSettingsValue

from .rq import enqueue
from .sync import push_user


def handle_post_save(sender, instance, *args, **kwargs):
    if settings.SYNC_TO_SHOWROOM:
        job_id = f'push_user_{instance.user.username}'
        enqueue(job_id, push_user, user=instance.user)


post_save.connect(
    handle_post_save,
    sender=UserPreferencesData,
    dispatch_uid='post_save_userpreferencesdata',
)
post_save.connect(
    handle_post_save,
    sender=UserSettingsValue,
    dispatch_uid='post_save_usersettingsvalue',
)


def create_user_preferences(sender, instance, *args, **kwargs):
    """Make sure that a user has a related UserPreferenceData object."""
    UserPreferencesData.objects.get_or_create(user=instance)


post_save.connect(
    create_user_preferences,
    sender=get_user_model(),
    dispatch_uid='post_save_create_userpreferencesdata',
)
