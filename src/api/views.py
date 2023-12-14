import json
from json import JSONDecodeError

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from user_preferences.models import (
    UserPreferencesData,
    UserSettings,
    UserSettingsValue,
    settings_dict,
)

from . import get_user_preferences_attributes
from .serializers.user_page import (
    UserImageSerializer,
    UserPreferencesDataSerializer,
    UserSerializer,
    UserSettingsSerializer,
)


class UserPreferencesDataViewSet(viewsets.GenericViewSet):
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
                except JSONDecodeError:
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


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer

    @extend_schema(
        tags=['user'],
    )
    def retrieve(self, request, *args, **kwargs):
        attributes = get_user_preferences_attributes(request.user)

        data = {
            'uuid': request.user.username,
            'name': request.user.get_full_name(),
            'email': attributes.get('email'),
            # TODO: update this, once permissions and groups are adapted
            'permissions': [],
            'profile': None,
            'space': settings.MAX_IMAGE_SIZE,
            'showroom_id': attributes.get('showroom_id'),
        }
        if hasattr(request.user, 'userpreferencesdata'):
            data['profile'] = request.user.userpreferencesdata.profile
        return Response(data)


class UserSettingsViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    lookup_field = 'user'
    '''
    retrieve:
    Returns certain user settings.

    update:
    Update certain user settings.

    '''

    serializer_class = UserSettingsSerializer
    queryset = UserSettingsValue.objects.all()
    parser_classes = (FormParser, MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    UserModel = get_user_model()
    http_method_names = ['get', 'put']

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
        ret = settings_dict(request.user)
        if not ret:
            return Response(
                _('No user settings exist'),
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ret)

    def destringify_value(self, v, value_type):
        bool_options = {'True': True, 'False': False}
        if value_type == 'boolean':
            v = bool_options[v.capitalize()]
        if value_type == 'list':
            try:
                v = json.loads(v.replace("'", '"'))
            except ValueError:
                return Response(
                    _(
                        'The given value type is not valid. Value must be: boolean, string, list (of strings). '
                        'Make sure field_type reflects your choice. '
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return v

    def validate_value(self, value, value_type):
        value_type_mapping = {
            'boolean': bool,
            'string': str,
            'list': list,
        }

        # if list, check if list of strings
        if isinstance(value, list):
            if not value or not all(
                isinstance(i, str) for i in value
            ):  # must be a list of strings
                return False

        if value_type not in value_type_mapping.keys():
            return False

        if not isinstance(value, value_type_mapping[value_type]):
            return False

        return True

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
        try:
            data = json.loads(request.data.get('data'))
        except json.decoder.JSONDecodeError:
            return Response('Invalid data', status=status.HTTP_400_BAD_REQUEST)

        for k, v in data.items():
            try:
                user_settings = UserSettings.objects.get(id=k)

                if self.validate_value(v, user_settings.value_type):
                    UserSettingsValue.objects.update_or_create(
                        user_settings=user_settings,
                        user=request.user,
                        defaults={
                            'value': v,
                        },
                    )
                else:
                    return Response(
                        _('Value %(value)s is not of type %(type)s')
                        % {'value': v, 'type': user_settings.value_type},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except UserSettings.DoesNotExist:
                return Response(
                    _('Setting %(setting)s does not exist') % {'setting': k},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(settings_dict(request.user))


class UserImageViewSet(viewsets.GenericViewSet, CreateModelMixin, DestroyModelMixin):
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


class UserPreferencesAgentViewSet(viewsets.GenericViewSet):
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
