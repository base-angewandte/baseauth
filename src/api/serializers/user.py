from collections import OrderedDict

from rest_framework.fields import CharField, IntegerField, ListField

from api.serializers import CleanModelSerializer, SwaggerMetaModelSerializer
from api.serializers.fields import ProfileField
from user_preferences.models import UserPreferencesData


class UserSerializer(CleanModelSerializer, SwaggerMetaModelSerializer):
    id = CharField(required=False)
    name = CharField(required=False)
    email = CharField(required=False)
    permissions = ListField(child=CharField(), required=False)
    space = IntegerField(required=False)
    profile = ProfileField()

    class Meta:
        model = UserPreferencesData
        fields = ('id', 'name', 'email', 'permissions', 'space', 'profile')

    swagger_meta_attrs = {
        'id': OrderedDict([('hidden', True)]),
        'name': OrderedDict([('hidden', True)]),
        'email': OrderedDict([('hidden', True)]),
        'permissions': OrderedDict([('hidden', True)]),
        'space': OrderedDict([('hidden', True)]),
    }
