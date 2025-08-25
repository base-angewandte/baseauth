from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

from django.conf import settings

from api.autocomplete.views import SUPPORTED_SOURCES

language_header_parameter = OpenApiParameter(
    name='Accept-Language',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=False,
    enum=list(settings.LANGUAGES_DICT.keys()),
)

fieldname_parameter = OpenApiParameter(
    name='fieldname',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    required=True,
    enum=SUPPORTED_SOURCES,
)
