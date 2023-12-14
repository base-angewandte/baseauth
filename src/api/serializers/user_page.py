import json

# import re
from collections import OrderedDict

import jsonschema
from drf_spectacular.utils import extend_schema_field
from jsonschema import validate
from rest_framework import serializers

from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from core.utils import placeholder_lazy
from user_preferences.models import UserPreferencesData, UserSettingsValue

from . import CleanModelSerializer, SwaggerMetaModelSerializer


def validate_json_field(value, schema):
    try:
        if not isinstance(value, list):
            value = [value]

        for v in value:
            validate(v, schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ValidationError(_(f'Well-formed but invalid JSON: {e}')) from e
    except json.decoder.JSONDecodeError as e:
        raise ValidationError(_(f'Poorly-formed text, not JSON: {e}')) from e
    except TypeError as e:
        raise ValidationError(f'Invalid characters: {e}') from e

    if len(value) > len({json.dumps(d, sort_keys=True) for d in value}):
        raise ValidationError(_('Data contains duplicate entries'))

    return value


@extend_schema_field(
    component_name='date_created',
    field={'type': 'string', 'x-attrs': {'hidden': True}},
)
class CustomDateCreated(serializers.DateTimeField):
    pass


@extend_schema_field(
    component_name='date_changed',
    field={'type': 'string', 'x-attrs': {'hidden': True}},
)
class CustomDateChanged(serializers.DateTimeField):
    pass


@extend_schema_field(
    component_name='expertise',
    field={
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'label': {
                    'type': 'object',
                    'properties': {
                        'fr': {'type': 'string'},
                        'en': {'type': 'string'},
                        'de': {'type': 'string'},
                    },
                },
                'source': {'type': 'string'},
                'source_name': {'type': 'string'},
            },
        },
        'x-attrs': {
            # TODO: activate the following, once the autosuggest routes are included
            # 'source': reverse_lazy(
            #     'lookup_all',
            #     kwargs={'version': 'v1', 'fieldname': 'expertise'},
            # ),
            'field_type': 'chips',
            # 'operationId': 'autosuggest_v1_lookup',
            'prefetch': ['source'],
            'order': 1,
            'allow_unknown_entries': False,
            'dynamic_autosuggest': True,
            'set_label_language': True,
            'sortable': True,
            'placeholder': placeholder_lazy(_('Skills and Expertise')),
        },
    },
)
class SkillsField(serializers.JSONField):
    pass


@extend_schema_field(
    component_name='complementary_email',
    field={
        'type': 'string',
        'x-attrs': {
            'order': 2,
            'placeholder': placeholder_lazy(_('E-Mail (complementary)')),
        },
    },
)
class CustomComplementaryEmail(serializers.CharField):
    pass


# @extend_schema_field(
#     component_name='urls',
#     field={
#         'type': 'array',
#         'items': {
#             'type': 'string',
#         },
#         'x-attrs': {
#             'order': 3,
#             'placeholder': placeholder_lazy(_('Website')),
#         },
#     },
# )
# class URLsField(serializers.JSONField):
#     pass


@extend_schema_field(
    component_name='urls',
    field={
        'type': 'string',
        'x-attrs': {
            'order': 3,
            'placeholder': placeholder_lazy(_('Website')),
        },
    },
)
class URLsField(serializers.URLField):
    pass


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


@extend_schema_field(
    component_name='data',
    field={
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'value': {'type': 'string'},
            'title': {'type': 'string'},
            'type': {'type': 'string'},
        },
        'x-attrs': {
            'placeholder': placeholder_lazy(_('Data')),
            'type': 'object',
            'properties': {
                'field_type': {'type': 'string'},
            },
        },
    },
)
class DataField(serializers.JSONField):
    pass


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


@extend_schema_field(
    component_name='profile',
    field={'type': 'object'}
    # todo: does it need more definition?
)
class ProfileField(serializers.JSONField):
    pass


class UserSerializer(CleanModelSerializer, SwaggerMetaModelSerializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    permissions = serializers.ListField(child=serializers.CharField(), required=False)
    space = serializers.IntegerField(required=False)
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


class UserImageSerializer(CleanModelSerializer, SwaggerMetaModelSerializer):
    class Meta:
        model = UserPreferencesData
        fields = ('user_image',)
