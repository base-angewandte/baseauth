from easy_thumbnails.files import get_thumbnailer

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import UserPreferencesData


@receiver(
    pre_save,
    sender=UserPreferencesData,
    dispatch_uid='pre_save_cleanup_thumbnail',
)
def cleanup_thumbnail(sender, instance, *args, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if obj.user_image and obj.user_image != instance.user_image:
            # Field has changed, cleanup thumbnail
            get_thumbnailer(obj.user_image).delete_thumbnails()


@receiver(
    post_save,
    sender=get_user_model(),
    dispatch_uid='post_save_create_userpreferencesdata',
)
def create_user_preferences(sender, instance, *args, **kwargs):
    """Make sure that a user has a related UserPreferenceData object."""
    UserPreferencesData.objects.get_or_create(user=instance)
