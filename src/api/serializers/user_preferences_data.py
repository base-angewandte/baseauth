from collections import OrderedDict

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from api.serializers import (
    CleanModelSerializer,
    SwaggerMetaModelSerializer,
    validate_json_field,
)
from api.serializers.fields import (
    CustomComplementaryEmail,
    CustomDateChanged,
    CustomDateCreated,
    SkillsField,
    URLsField,
)
from core.utils import placeholder_lazy
from user_preferences.models import UserPreferencesData


class UserPreferencesDataSerializer(CleanModelSerializer, SwaggerMetaModelSerializer):
    date_created = CustomDateCreated(read_only=True, format='%Y-%m-%d')
    date_changed = CustomDateChanged(read_only=True, format='%Y-%m-%d')
    complementary_email = CustomComplementaryEmail(
        label=_('E-Mail (complementary)'),
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    # urls = URLsField(
    #     label=_('URL'),
    #     required=False,
    #     default=None,
    # )
    urls = URLsField(
        label=_('URL'), required=False, default='', allow_blank=True, allow_null=True
    )
    expertise = SkillsField(
        label=_('Skills and Expertise'),
        required=False,
        allow_null=True,
        default=[],
    )

    def validate_expertise(self, value):
        schema = {
            'additionalProperties': False,
            'type': 'object',
            'properties': {
                'label': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'fr': {'type': 'string'},
                        'en': {'type': 'string'},
                        'de': {'type': 'string'},
                        'additionalProperties': False,
                    },
                },
                'source': {'type': 'string'},
                'source_name': {'type': 'string'},
                'additionalProperties': False,
            },
        }

        return validate_json_field(value, schema)

    # def validate_urls(self, value):
    #     if value:
    #         urls = ', '.join(value.split(','))
    #         urls = re.findall(
    #             r'[(https://)|\w]*?[\w]*\.[-/\w]*\.\w*[(/{1})]?[#-\./\w]*[(/{1,})]?',
    #             urls,
    #         )
    #         return [url.replace(',', '') for url in urls] if urls else []
    #     return []

    class Meta:
        model = UserPreferencesData
        fields = (
            'expertise',
            'complementary_email',
            'urls',
            'date_created',
            'date_changed',
        )

        swagger_meta_attrs = {
            'date_created': OrderedDict([('hidden', True)]),
            'date_changed': OrderedDict([('hidden', True)]),
            'expertise': OrderedDict(
                [
                    ('field_type', 'chips'),
                    (
                        'operationId',
                        'autosuggest_v1_lookup',
                    ),
                    (
                        'source',
                        reverse_lazy(
                            'lookup_all',
                            kwargs={'version': 'v1', 'fieldname': 'expertise'},
                        ),
                    ),
                    ('prefetch', ['source']),
                    ('order', 1),
                    ('allow_unknown_entries', False),
                    (
                        'dynamic_autosuggest',
                        True,
                    ),
                    (
                        'set_label_language',
                        True,
                    ),
                    (
                        'sortable',
                        True,
                    ),
                    ('placeholder', placeholder_lazy(_('Skills and Expertise'))),
                ]
            ),
            'complementary_email': OrderedDict(
                [
                    ('order', 2),
                    ('placeholder', placeholder_lazy(_('E-Mail (complementary)'))),
                ]
            ),
            'urls': OrderedDict(
                [
                    ('order', 3),
                    ('placeholder', placeholder_lazy(_('URL'))),
                    # ('field_format', 'half'),
                ]
            ),
        }
