from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from api import get_user_preferences_attributes
from api.serializers.user_preferences_data import UserPreferencesDataSerializer
from user_preferences.models import UserPreferencesData


class UserPreferencesAgentViewSet(GenericViewSet):
    queryset = UserPreferencesData.objects.all()
    serializer_class = UserPreferencesDataSerializer
    permission_classes = [HasAPIKey | IsAuthenticated]

    @extend_schema(
        tags=['user'],
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
        except APIKey.DoesNotExist:
            raise PermissionDenied from None
        UserModel = get_user_model()
        try:
            return Response(
                get_user_preferences_attributes(UserModel.objects.get(username=pk))
            )
        except UserModel.DoesNotExist:
            return Response(
                _('User does not exist'),
                status=status.HTTP_404_NOT_FOUND,
            )
