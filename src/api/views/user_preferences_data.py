import json

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.utils.translation import gettext_lazy as _

from api.serializers.user_preferences_data import UserPreferencesDataSerializer
from user_preferences.models import UserPreferencesData


class UserPreferencesDataViewSet(GenericViewSet):
    serializer_class = UserPreferencesDataSerializer
    queryset = UserPreferencesData.objects.all()
    parser_classes = (FormParser, MultiPartParser)
    filter_backends = (DjangoFilterBackend,)

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(
                description=_('User preferences object does not exist'),
            ),
        },
    )
    def retrieve(self, request, **kwargs):
        """Returns the currently logged in user."""
        if UserPreferencesData.objects.filter(user=request.user).exists():
            user_preferences = self.queryset.get(user=request.user)
            if user_preferences:
                serializer = UserPreferencesDataSerializer(user_preferences).data
                return Response(serializer)

        raise NotFound(_('User preferences object does not exist'))

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(
                description=_('User preferences object does not exist'),
            ),
        },
    )
    def _update(self, request, *args, partial=False, **kwargs):
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
            if 'expertise' in data and (
                data['expertise'] == '' or data['expertise'] is None
            ):
                data['expertise'] = []

            serializer = self.get_serializer(data=data, partial=partial)

            if serializer.is_valid():
                if serializer.validated_data:
                    user_preferences.__dict__.update(serializer.validated_data)
                    user_preferences.save()

                return Response(UserPreferencesDataSerializer(user_preferences).data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raise NotFound(_('User preferences object does not exist'))

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(
                description=_('User preferences object does not exist'),
            ),
        },
    )
    def update(self, request, *args, **kwargs):
        """Update the currently logged in user."""
        return self._update(request, *args, partial=False, **kwargs)

    @extend_schema(
        tags=['user'],
        request=serializer_class,
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(
                description=_('User preferences object does not exist'),
            ),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update the currently logged in user."""
        return self._update(request, *args, partial=True, **kwargs)
