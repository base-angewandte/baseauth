import json

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import UpdateModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from api.serializers.user_page import UserSettingsSerializer
from user_preferences.models import UserSettings, UserSettingsValue, settings_dict


class UserSettingsViewSet(GenericViewSet, UpdateModelMixin):
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
