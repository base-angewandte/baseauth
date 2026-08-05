from api.serializers import CleanModelSerializer, SwaggerMetaModelSerializer
from user_preferences.models import UserPreferencesData


class UserImageSerializer(CleanModelSerializer, SwaggerMetaModelSerializer):
    class Meta:
        model = UserPreferencesData
        fields = ('user_image',)
