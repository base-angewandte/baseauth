from easy_thumbnails.files import get_thumbnailer

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page

from .models import UserPreferencesData


@cache_page(60 * 15)
def user_image(request, image):
    try:
        user_preferences = UserPreferencesData.objects.get(user_image=image)
        return redirect(
            request.build_absolute_uri(
                get_thumbnailer(user_preferences.user_image)
                .get_thumbnail(settings.THUMBNAIL_OPTIONS)
                .url
            )
        )
    except UserPreferencesData.DoesNotExist:
        raise Http404 from None
