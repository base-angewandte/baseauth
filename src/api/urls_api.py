from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from .views.autosuggest_lookup import lookup_view
from .views.autosuggest_lookup_search import lookup_view_search
from .views.autosuggest_user import autosuggest_user
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
    # Autosuggest routes
    re_path(
        r'^autosuggest/(?P<fieldname>({}))/$'.format(
            '|'.join(settings.ACTIVE_SOURCES.keys())
        ),
        lookup_view,
        name='lookup_all',
    ),
    re_path(
        r'^autosuggest/(?P<fieldname>({}))/(?P<searchstr>(.*))/$'.format(
            '|'.join(settings.ACTIVE_SOURCES.keys())
        ),
        lookup_view_search,
        name='lookup',
    ),
    re_path(
        r'^autosuggest/(?P<user>(.*))/$',
        autosuggest_user,
        name='autosuggest_user',
    ),
    # Open API routes
    path('schema/openapi3.yaml', SpectacularAPIView.as_view(), name='schema-yaml'),
    path('schema/openapi3.json', SpectacularJSONAPIView.as_view(), name='schema-json'),
    path(
        'schema/swagger-ui',
        SpectacularSwaggerView.as_view(url_name='schema-json'),
        name='swagger-ui',
    ),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
