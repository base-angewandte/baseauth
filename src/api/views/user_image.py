from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from api.serializers.user_image import UserImageSerializer
from user_preferences.models import UserPreferencesData


class UserImageViewSet(GenericViewSet, CreateModelMixin, DestroyModelMixin):
    """
    retrieve:
    Returns certain profile photo / thumbnail.

    create:
    Upload a profile photo.

    delete:
    Delete a profile photo.

    """

    serializer_class = UserImageSerializer
    parser_classes = (
        FormParser,
        MultiPartParser,
        FileUploadParser,
    )
    filter_backends = (DjangoFilterBackend,)
    queryset = UserPreferencesData.objects.all()

    @extend_schema(
        tags=['user'],
        methods=['GET'],
        request=serializer_class,
        operation_id='user_image_read',
        responses={
            200: OpenApiResponse(description=''),
            403: OpenApiResponse(description='Access not allowed'),
            404: OpenApiResponse(description='User preferences object not found'),
        },
    )
    def list(self, request, *args, **kwargs):
        try:
            user_preferences = UserPreferencesData.objects.get(user=request.user)

            if user_preferences.user_image:
                return Response(
                    reverse('user_image', kwargs={'image': user_preferences.user_image})
                )

            return Response(
                _('User image does not exist.'), status=status.HTTP_404_NOT_FOUND
            )

        except UserPreferencesData.DoesNotExist:
            return Response(
                _('User preferences do not exist.'), status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=['user'],
        methods=['POST'],
        parameters=[
            OpenApiParameter(
                name='user_image',
                type=OpenApiTypes.BINARY,
                required=False,
                description='Profile photo',
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        user_preferences = UserPreferencesData.objects.get(user=request.user)
        if user_preferences:
            serializer = UserImageSerializer(data=request.data)

            if serializer.is_valid():
                if serializer.validated_data:
                    if request.FILES.get('user_image'):
                        user_preferences.user_image = request.FILES['user_image']
                        user_preferences.save()
                        return Response(
                            reverse(
                                'user_image',
                                kwargs={'image': user_preferences.user_image},
                            )
                        )

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
    def delete(self, request, *args, **kwargs):
        # DELETE method cannot work without ID parameter
        user_preferences = UserPreferencesData.objects.get(user=request.user)
        if user_preferences:
            user_preferences.user_image.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            _('User preferences do not exist'), status=status.HTTP_404_NOT_FOUND
        )
