from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.conf import settings
from django.utils.module_loading import import_string

from api.spectacular import fieldname_parameter, language_header_parameter
from api.views import fetch_responses


@extend_schema(
    tags=['autosuggest'],
    parameters=[fieldname_parameter, language_header_parameter],
    operation_id='autosuggest_v1_lookup_all',
)
@api_view(['GET'])
def lookup_view(request, fieldname, *args, **kwargs):
    source = settings.ACTIVE_SOURCES.get(fieldname, ())

    if isinstance(source, dict):
        source = source.get('all', ())

    if isinstance(source, str):
        data = import_string(source)()
    else:
        data = fetch_responses('', source)
    return Response(data)
