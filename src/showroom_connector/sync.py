import requests

from django.conf import settings

from api import get_user_preferences_attributes
from showroom_connector.exceptions import (
    ShowroomAuthenticationException,
    ShowroomException,
    ShowroomUndefinedException,
)
from user_preferences.models import UserPreferencesData

auth_headers = {
    'X-Api-Key': settings.SHOWROOM_API_KEY,
}


def push_user(user):
    # ensure we always push the latest data
    user.refresh_from_db()

    data = get_user_preferences_attributes(user)

    r = requests.put(
        f'{settings.SHOWROOM_API_BASE}entities/{user.username}/',
        json=data,
        headers=auth_headers,
        timeout=settings.REQUESTS_TIMEOUT,
    )

    if r.status_code == 403:
        raise ShowroomAuthenticationException(f'Authentication failed: {r.text}')

    elif r.status_code == 400:
        raise ShowroomException(
            f'User {user.username} could not be pushed: 400: {r.text}'
        )

    elif r.status_code in [200, 201]:
        showroom_id = r.json()
        UserPreferencesData.objects.filter(pk=user.userpreferencesdata.pk).update(
            showroom_id=showroom_id
        )
        return showroom_id
    else:
        raise ShowroomUndefinedException(
            f'Ouch! Something unexpected happened: {r.status_code} {r.text}'
        )
