from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in, dispatch_uid="process_user_attributes")
def process_user_attributes(sender, user, *args, **kwargs):
    if not user:
        return

    if user.username in settings.SUPERUSERS:
        user.is_staff = True
        user.is_superuser = True
        user.save()
    else:
        user.is_staff = False
        user.is_superuser = False
        user.save()
