from django.urls import include, re_path

urlpatterns = [
    re_path(r'^api/(?P<version>v2)/', include('api.urls_api_v2')),
]
