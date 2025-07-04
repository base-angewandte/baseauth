from django.urls import include, re_path

from . import urls_api, urls_api_v2

urlpatterns = [
    re_path(r'^(?P<version>(v1))/', include(urls_api)),
    # Api autocomplete v2 url
    re_path(r'^(?P<version>(v2))/', include(urls_api_v2)),
]
