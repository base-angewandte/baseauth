from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularSwaggerView,
)

from django.urls import include, re_path

V1_PATTERNS = [re_path(r'^api/(?P<version>v1)/', include('api.urls_api'))]
V2_PATTERNS = [re_path(r'^api/(?P<version>v2)/', include('api.urls_api_v2'))]


class VersionedSchemaGenerator(SchemaGenerator):
    expected_prefix: str = '/'
    other_prefixes: tuple[str, ...] = ()

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request=request, public=public)

        # Normalize access to "paths"
        def get_paths(s):
            if s is None:
                return None
            if hasattr(s, 'paths'):
                return s.paths
            if isinstance(s, dict):
                return s.get('paths')
            return None

        def set_paths(s, new_paths):
            if hasattr(s, 'paths'):
                s.paths = new_paths
            elif isinstance(s, dict):
                s['paths'] = new_paths

        paths = get_paths(schema)
        if not paths:
            return schema

        expected = self.expected_prefix
        others = tuple(self.other_prefixes) if self.other_prefixes else ()

        new_paths = {}
        for path, item in list(paths.items()):
            p = str(path)

            if p.startswith(expected):
                new_paths[p] = item
                continue

            for other in others:
                if p.startswith(other):
                    new_p = expected + p[len(other) :]
                    new_paths[new_p] = item
                    break

        set_paths(schema, new_paths)
        return schema


class V1Gen(VersionedSchemaGenerator):
    expected_prefix = '/api/v1/'
    other_prefixes = ('/api/v2/',)


class V2Gen(VersionedSchemaGenerator):
    expected_prefix = '/api/v2/'
    other_prefixes = ('/api/v1/',)


# v2 schema and docs
no_ui_view = SpectacularAPIView.as_view(
    patterns=V1_PATTERNS,
    generator_class=V1Gen,
)
schema_json_v1_view = SpectacularJSONAPIView.as_view(
    patterns=V1_PATTERNS,
    generator_class=V1Gen,
)
swagger_view = SpectacularSwaggerView.as_view(url='/api/v1/openapi.json')

# v2 schema and docs
no_ui_view_v2 = SpectacularAPIView.as_view(
    patterns=V2_PATTERNS,
    generator_class=V2Gen,
)
schema_json_v2_view = SpectacularJSONAPIView.as_view(
    patterns=V2_PATTERNS,
    generator_class=V2Gen,
)
swagger_view_v2 = SpectacularSwaggerView.as_view(url='/api/v2/openapi.json')
