from api.serializers import (
    CleanModelSerializer,
    SwaggerMetaModelSerializer,
    validate_json_field,
)
from api.serializers.fields import DataField
from user_preferences.models import UserSettingsValue


class UserSettingsSerializer(CleanModelSerializer, SwaggerMetaModelSerializer):
    data = DataField(required=False)

    def validate_data(self, value):
        schema = {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'id': {'type': 'string'},
                'value': {'type': 'string'},
                'title': {'type': 'string'},
                'type': {'type': 'string'},
            },
            'x-attrs': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'field_type': {'type': 'string'},
                },
            },
        }

        return validate_json_field(value, schema)

    class Meta:
        model = UserSettingsValue
        fields = ('data',)
