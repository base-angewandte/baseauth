import logging

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import translation
from django.utils.module_loading import import_string

from api.serializers.autosuggest import (
    AutosuggestUserSerializer,
)
from api.views import fetch_responses
from core.skosmos import autosuggest

logger = logging.getLogger(__name__)

type_parameter = openapi.Parameter(
    'type',
    openapi.IN_QUERY,
    description='',
    required=True,
    type=openapi.TYPE_STRING,
    enum=[*list(settings.ACTIVE_SOURCES.keys()), 'users'],
)

q_parameter = openapi.Parameter(
    'q',
    openapi.IN_QUERY,
    description='Search query string.',
    required=False,
    type=openapi.TYPE_STRING,
)
limit_parameter = OpenApiParameter(
    name='limit',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
)
language_header_parameter = openapi.Parameter(
    'Accept-Language',
    openapi.IN_HEADER,
    required=False,
    type=openapi.TYPE_STRING,
    enum=['de', 'en'],
)


@swagger_auto_schema(
    methods=['get'],
    manual_parameters=[
        type_parameter,
        q_parameter,
        limit_parameter,
        language_header_parameter,
    ],
)
@extend_schema(
    tags=['autocomplete'],
    parameters=[
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            enum=[*list(settings.ACTIVE_SOURCES.keys()), 'users'],
        ),
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        limit_parameter,
        OpenApiParameter(
            name='Accept-Language',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=False,
            enum=['de', 'en'],
        ),
    ],
    responses={'200': AutosuggestUserSerializer(many=True)},
    operation_id='autosuggest_v2_autocomplete',
)
@api_view(['GET'])
def autocomplete(request, *args, **kwargs):
    try:
        limit = int(request.GET.get('limit', 10))
        if limit <= 0:
            raise ValueError
    except ValueError as e:
        raise ParseError('limit must be a positive integer') from e

    lang = request.headers.get('Accept-Language', '')

    if lang not in {'de', 'en'}:
        lang = 'en'

    translation.activate(lang)

    source_type = request.GET.get('type')
    q_param = request.GET.get('q', '')

    if not source_type:
        return Response({'error': 'Missing required "type" parameter.'}, status=400)

    if source_type == 'users':
        if not q_param:
            return Response([])

        User = get_user_model()  # noqa: N806
        users = User.objects.filter(
            Q(first_name__icontains=q_param) | Q(last_name__icontains=q_param),
        ).only('username', 'first_name', 'last_name')[:limit]

        return Response(
            [
                {
                    'UUID': u.username,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'label': u.get_full_name(),
                }
                for u in users
            ],
        )

    source = settings.ACTIVE_SOURCES.get(source_type, ())

    if not q_param and isinstance(source, dict):
        source = source.get('all', ())
    if q_param and isinstance(source, dict):
        source = source.get('search', ())

    if isinstance(source, str):
        data = (
            autosuggest(import_string(source)(), q_param)
            if q_param
            else import_string(source)()
        )
    else:
        data = fetch_responses(q_param, source)

    return Response(data[:limit])
