from shibboleth.middleware import ShibbolethRemoteUserMiddleware as ShibbolethMiddleware

from django.conf import settings


class ShibbolethRemoteUserMiddleware(ShibbolethMiddleware):
    header = settings.SHIBBOLETH_REMOTE_USER_HEADER
