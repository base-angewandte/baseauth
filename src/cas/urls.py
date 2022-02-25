"""CAS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from mama_cas.views import LoginView

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from core.views import locked_out

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url=settings.HOME_REDIRECT, permanent=False),
        name="index",
    ),
    # admin
    path("admin/", admin.site.urls),
    # views
    path("", include("mama_cas.urls")),
    path("captcha/", include("captcha.urls")),
    path("locked/", locked_out, name="locked_out"),
    # i18n
    path("i18n/", include("django.conf.urls.i18n")),
]


if settings.SHIBBOLETH_AUTHENTICATION:
    urlpatterns.insert(
        2, re_path(r"^login/?$", login_required(LoginView.as_view()), name="cas_login")
    )
    urlpatterns += [
        path("shib/", include("shibboleth.urls", namespace="shibboleth")),
    ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
