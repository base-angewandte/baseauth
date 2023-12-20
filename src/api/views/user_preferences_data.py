import json

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from api.serializers.user_page import UserPreferencesDataSerializer
from user_preferences.models import UserPreferencesData


class UserPreferencesDataViewSet(GenericViewSet):
    """
    retrieve:
    Returns the currently logged in user.

    update:
    Update the currently logged in user.

    partial_update:
    Partially update the currently logged in user.
    """

    serializer_class = UserPreferencesDataSerializer
    queryset = UserPreferencesData.objects.all()
    parser_classes = (FormParser, MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    UserModel = get_user_model()

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(description='User preferences object not found'),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        if UserPreferencesData.objects.filter(user=request.user).exists():
            user_preferences = self.queryset.get(user=request.user)
            if user_preferences:
                serializer = UserPreferencesDataSerializer(user_preferences).data
                return Response(serializer)

        return Response(
            _('User preferences object does not exist'),
            status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(description='User preferences object not found'),
        },
    )
    def _update(self, request, partial=False, *args, **kwargs):
        user_preferences = UserPreferencesData.objects.get(user=request.user)
        if user_preferences:
            # TODO: get rid of this quick fix again
            data = {}
            for k, v in request.data.items():
                try:
                    data[k] = json.loads(v)
                except json.JSONDecodeError:
                    data[k] = v

            # If value is empty, change expertise's default to []
            if (
                'expertise' in data.keys()
                and data['expertise'] == ''
                or data['expertise'] is None
            ):
                data['expertise'] = []

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                if serializer.validated_data:
                    user_preferences.__dict__.update(serializer.validated_data)
                    user_preferences.save()

                return Response(UserPreferencesDataSerializer(user_preferences).data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            _('User preferences do not exist'), status=status.HTTP_404_NOT_FOUND
        )

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(description='User preferences object not found'),
        },
    )
    def update(self, request, *args, **kwargs):
        return self._update(request, partial=False, *args, **kwargs)

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(description='User preferences object not found'),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return self._update(request, partial=True, *args, **kwargs)
