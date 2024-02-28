from easy_thumbnails.files import get_thumbnailer

from django.db.models.signals import pre_save
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
