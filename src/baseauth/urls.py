"""CAS URL Configuration.

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
from mama_cas.views import (
    LoginView,
    LogoutView,
    ProxyValidateView,
    ProxyView,
    SamlValidateView,
    ServiceValidateView,
    ValidateView,
    WarnView,
)

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView

from core.views import locked_out

urlpatterns = [
    path(
        '',
        RedirectView.as_view(url=settings.HOME_REDIRECT, permanent=False),
        name='index',
    ),
    # admin
    path('admin/', admin.site.urls),
    # mama-cas views
    path('validate/', ValidateView.as_view(), name='cas_validate'),
    path(
        'serviceValidate/',
        ServiceValidateView.as_view(),
        name='cas_service_validate',
    ),
    path('proxyValidate/', ProxyValidateView.as_view(), name='cas_proxy_validate'),
    path('proxy/', ProxyView.as_view(), name='cas_proxy'),
    path(
        'p3/serviceValidate/',
        ServiceValidateView.as_view(),
        name='cas_p3_service_validate',
    ),
    path(
        'p3/proxyValidate/',
        ProxyValidateView.as_view(),
        name='cas_p3_proxy_validate',
    ),
    path('warn/', WarnView.as_view(), name='cas_warn'),
    path('samlValidate/', SamlValidateView.as_view(), name='cas_saml_validate'),
    path('captcha/', include('captcha.urls')),
    path('locked/', locked_out, name='locked_out'),
    # i18n
    path('i18n/', include('django.conf.urls.i18n')),
]

# if cas-auth (based on django-cas-ng) is not used, we provide standard mama-cas paths
if 'cas' not in settings.AUTH_BACKENDS_TO_USE:
    urlpatterns += [
        path('login/', LoginView.as_view(), name='cas_login'),
        path('logout/', LogoutView.as_view(), name='cas_logout'),
    ]

# otherwise django-cas-ng is used to authenticate against another CAS server
else:
    import django_cas_ng.views

    urlpatterns += [
        path('login/', login_required(LoginView.as_view()), name='cas_login'),
        path(
            'logout/',
            RedirectView.as_view(url=reverse_lazy('cas_ng_logout')),
            name='cas_logout',
        ),
        path(
            'accounts/login/',
            django_cas_ng.views.LoginView.as_view(),
            name='cas_ng_login',
        ),
        path(
            'accounts/logout/',
            django_cas_ng.views.LogoutView.as_view(),
            name='cas_ng_logout',
        ),
        path(
            'accounts/callback/',
            django_cas_ng.views.CallbackView.as_view(),
            name='cas_ng_proxy_callback',
        ),
    ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
