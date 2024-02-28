from django.conf import settings
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
