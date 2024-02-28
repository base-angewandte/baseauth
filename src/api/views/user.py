from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.conf import settings

from api import get_user_preferences_attributes
from api.serializers.user import UserSerializer


class UserViewSet(GenericViewSet):
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
