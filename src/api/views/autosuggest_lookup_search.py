from rest_framework import status as drf_status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.conf import settings
from django.utils.module_loading import import_string

from core.skosmos import autosuggest


@api_view(['GET'])
def lookup_view_search(request, fieldname, searchstr='', *args, **kwargs):
    source = settings.ACTIVE_SOURCES.get(fieldname)
    if isinstance(source, dict):
        source = source.get('search')

    if not isinstance(source, str):
        return Response([], status=drf_status.HTTP_200_OK)

    obj = import_string(source)

    if callable(obj):
        try:
            return Response(obj(searchstr or ''))
        except TypeError:
            pass

    provider = obj()
    data = autosuggest(provider, searchstr or '')
    return Response(data)
