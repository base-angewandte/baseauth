import logging

from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Q

from api.serializers.autosuggest import (
    AutosuggestUserSerializer,
)
from core.pagination import EnvelopePagination
from core.skosmos import autosuggest, get_base_keywords, get_skills

from .serializers import (
    SOURCES,
    AutocompleteRequestSerializer,
)

logger = logging.getLogger(__name__)

type_parameter = OpenApiParameter(
    name='type',
    location=OpenApiParameter.QUERY,
    required=True,
    type={'type': 'array', 'items': {'type': 'string', 'enum': SOURCES}},
    style='form',
    explode=False,
)


@extend_schema(
    tags=['autocomplete'],
    parameters=[
        AutocompleteRequestSerializer,
        type_parameter,
    ],
    responses={200: AutosuggestUserSerializer(many=True)},
    operation_id='autosuggest_v2_autocomplete',
)
@swagger_auto_schema(
    methods=['get'],
    query_serializer=AutocompleteRequestSerializer,
    manual_parameters=[type_parameter],
)
@api_view(['GET'])
def autocomplete(request, *args, **kwargs):
    try:
        limit = int(request.GET.get('limit', 10))
        if limit <= 0:
            raise ValueError
    except ValueError as exc:
        raise ParseError('limit must be a positive integer') from exc

    serializer = AutocompleteRequestSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    limit = data['limit']
    q_param = data.get('q', '')
    type_list = data['type'].split(',')

    results = {}
    pagination = {}
    paginator = EnvelopePagination()
    paginator.default_limit = limit

    for source_type in type_list:
        if source_type == 'users':
            User = get_user_model()  # noqa: N806
            users_qs = User.objects.filter(
                Q(first_name__icontains=q_param) | Q(last_name__icontains=q_param),
            ).only('username', 'first_name', 'last_name')[:limit]

            page = paginator.paginate_queryset(users_qs, request)
            data = [
                {
                    'UUID': u.username,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'label': u.get_full_name(),
                    'source_name': 'base',
                }
                for u in page
            ]

        elif source_type == 'expertise':
            suggestions = (
                autosuggest(get_skills(), q_param) if q_param else get_base_keywords()
            )
            page = paginator.paginate_queryset(suggestions, request)
            data = list(page)

        paged = paginator.get_paginated_response(data).data
        results[source_type] = paged['results']
        pagination[source_type] = {
            k: paged[k] for k in ('total', 'offset', 'limit', 'result_count')
        }

    meta = {
        'types': list(results.keys()),
        'pagination': pagination,
    }
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang:
        meta['language'] = lang

    data_block = next(iter(results.values())) if len(results) == 1 else results

    envelope = {
        'status': 'success',
        'code': 200,
        'msg': 'OK',
        'meta': meta,
        'data': data_block,
    }
    return Response(envelope, status=200)
