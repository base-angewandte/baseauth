from drf_spectacular.utils import OpenApiParameter, OpenApiTypes  # extend_schema

from django.conf import settings

language_header_parameter = OpenApiParameter(
    name='Accept-Language',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=False,
    enum=list(settings.LANGUAGES_DICT.keys()),
)
