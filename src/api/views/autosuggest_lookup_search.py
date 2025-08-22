from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.utils.module_loading import import_string

from api.autocomplete.views import SUPPORTED_SOURCES
from api.serializers.autosuggest import AutosuggestFieldSerializer
from api.spectacular import fieldname_parameter, language_header_parameter
from api.views import fetch_responses
from core.skosmos import autosuggest


@extend_schema(
    tags=['autosuggest'],
    parameters=[fieldname_parameter, language_header_parameter],
    responses={
        '200': AutosuggestFieldSerializer(many=True),
    },
    operation_id='autosuggest_v1_lookup',
)
@api_view(['GET'])
def lookup_view_search(request, fieldname, searchstr='', *args, **kwargs):
    source = SUPPORTED_SOURCES.get(fieldname, ())

    if isinstance(source, dict):
        source = source.get('search', ())

    if isinstance(source, str):
        data = autosuggest(import_string(source)(), searchstr)
    else:
        data = fetch_responses(searchstr, source)

    return Response(data)
