from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from api import get_user_preferences_attributes
from api.serializers.user_preferences_data import UserPreferencesDataSerializer
from core.pagination import EnvelopePagination
from user_preferences.models import UserPreferencesData


class UserPreferencesAgentViewSet(GenericViewSet):
    queryset = UserPreferencesData.objects.all()
    serializer_class = UserPreferencesDataSerializer
    pagination_class = EnvelopePagination
    permission_classes = [HasAPIKey | IsAuthenticated]

    @extend_schema(
        tags=['users'],
        parameters=[
            OpenApiParameter(
                name='X-Api-Key',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
            ),
        ],
    )
    def retrieve(self, request, pk=None, *args, **kwargs):
        key = request.headers.get('X-Api-Key', '')
        try:
            APIKey.objects.get_from_key(key)
        except APIKey.DoesNotExist as err:
            raise PermissionDenied from err
        User = get_user_model()  # noqa: N806 - this represents a model class
        try:
            return Response(
                get_user_preferences_attributes(User.objects.get(username=pk)),
            )
        except User.DoesNotExist as err:
            raise NotFound(_('User does not exist')) from err
