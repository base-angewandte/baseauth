from django.conf import settings as django_settings


def settings(request):
    return {
        "SHIBBOLETH_AUTHENTICATION": django_settings.SHIBBOLETH_AUTHENTICATION,
        "LOGOUT_URL": getattr(django_settings, "LOGOUT_URL", ""),
    }
