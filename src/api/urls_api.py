from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views.user import UserViewSet
from .views.user_image import UserImageViewSet
from .views.user_preferences_agent import UserPreferencesAgentViewSet
from .views.user_preferences_data import UserPreferencesDataViewSet
from .views.user_settings import UserSettingsViewSet

router = routers.DefaultRouter()

router.register(r'users', UserPreferencesAgentViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('user/', UserViewSet.as_view({'get': 'retrieve'}), name='user'),
    path(
        'user/data/',
        UserPreferencesDataViewSet.as_view(
            {
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
            }
        ),
        name='user_data',
    ),
    path(
        'user/settings/',
        UserSettingsViewSet.as_view(
            {
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
            }
        ),
        name='user_settings',
    ),
    path(
        'user/image/',
        UserImageViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'delete'}),
        name='user_image',
    ),
    # TODO: integrate from autosuggest package in cas repo
    # path('autosuggest/', include('autosuggest.urls')),
    path('schema/openapi3.yaml', SpectacularAPIView.as_view(), name='schema-yaml'),
    path('schema/openapi3.json', SpectacularJSONAPIView.as_view(), name='schema-json'),
    path(
        'schema/swagger-ui',
        SpectacularSwaggerView.as_view(url_name='schema-json'),
        name='swagger-ui',
    ),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
