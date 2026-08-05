from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Q

from api.serializers.autosuggest import AutosuggestUserSerializer


@extend_schema(
    tags=['autosuggest'],
    parameters=[
        OpenApiParameter(
            name='user',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
    responses={
        '200': AutosuggestUserSerializer(many=True),
    },
    operation_id='autosuggest_user_all',
)
@api_view(['GET'])
def autosuggest_user(request, user, *args, **kwargs):
    """Get autosuggest results for query."""
    User = get_user_model()  # noqa: N806 - this represents the model class
    # the user parameter of this endpoint is the actual string to search for
    searchstr = user

    # TODO: add search for ldap users if ldap is enabled

    search_result = User.objects.filter(
        Q(first_name__icontains=searchstr) | Q(last_name__icontains=searchstr),
    )
    response = [
        {
            'UUID': user.username,  # TODO: discuss in review: should this be all caps? leaving for now, as frontend might depend on it
            'first_name': user.first_name,
            'last_name': user.last_name,
            'label': user.get_full_name(),
        }
        for user in search_result
    ]

    return Response(response)
