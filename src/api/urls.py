from django.urls import include, path, re_path

from . import urls_api as v1_urls, urls_api_v2 as v2_urls
from .openapi_schemas import (
    no_ui_view,
    no_ui_view_v2,
    schema_json_v1_view,
    schema_json_v2_view,
    swagger_view,
    swagger_view_v2,
)

urlpatterns = [
    path('v2/openapi.json', schema_json_v2_view, name='schema-json-v2'),
    path('v1/openapi.json', schema_json_v1_view, name='schema-json-v1'),
    # v1
    re_path(
        r'^(?P<version>v1)/openapi(?P<format>\.json|\.yaml)$',
        no_ui_view,
        name='schema',
    ),
    path('v1/docs/', swagger_view, name='schema-docs'),
    re_path(r'^(?P<version>(v1))/', include((v1_urls, 'api'), namespace='v1')),
    # v2
    re_path(
        r'^(?P<version>v2)/openapi(?P<format>\.json|\.yaml)$',
        no_ui_view_v2,
        name='schema_v2',
    ),
    path('v2/docs/', swagger_view_v2, name='schema-docs-v2'),
    re_path(r'^(?P<version>(v2))/', include((v2_urls, 'api'), namespace='v2')),
]
