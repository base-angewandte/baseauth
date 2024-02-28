from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def user_hash(username):
    return settings.HASHIDS.encode_hex(username.encode('utf-8').hex())


def decode_user_hash(hash):
    return bytes.fromhex(settings.HASHIDS.decode_hex(hash)).decode('utf-8')


def get_quota_for_user(user):
    cache_key = f'{user.username}_quota'
    quota = cache.get(cache_key)
    if not quota:
        joined = user.date_joined
        today = timezone.now()
        diff = (
            today.year
            - joined.year
            - ((today.month, today.day) < (joined.month, joined.day))
        )
        quota = settings.USER_QUOTA * (diff + 1)
        cache.set(cache_key, quota, 86400)
    return quota
