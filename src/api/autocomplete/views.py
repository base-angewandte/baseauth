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

from django.contrib.auth import get_user_model
from django.db.models import Q

from api.serializers.autosuggest import (
    AutosuggestUserSerializer,
)
from core.skosmos import autosuggest, get_base_keywords, get_skills

logger = logging.getLogger(__name__)

SUPPORTED_SOURCES = ('expertise', 'users')

type_parameter = openapi.Parameter(
    'type',
    openapi.IN_QUERY,
    description='',
    required=True,
    enum=SUPPORTED_SOURCES,
    type=openapi.TYPE_STRING,
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


@swagger_auto_schema(
    methods=['get'],
    manual_parameters=[
        type_parameter,
        q_parameter,
        limit_parameter,
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
            enum=SUPPORTED_SOURCES,
        ),
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        limit_parameter,
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

    source_type = request.GET.get('type')
    q_param = request.GET.get('q', '')

    if source_type not in SUPPORTED_SOURCES:
        return Response(
            {'error': f'Unknown type "{source_type}". Allowed: {SUPPORTED_SOURCES}'},
            status=400,
        )

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
    if source_type == 'expertise':
        if q_param:
            suggestions = autosuggest(get_skills(), q_param)
        else:
            suggestions = get_base_keywords()

        return Response(suggestions[:limit])

    return Response([], status=204)
