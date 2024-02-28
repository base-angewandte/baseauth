from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from core.utils import placeholder_lazy


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


@extend_schema_field(
    component_name='profile',
    field={'type': 'object'}
    # todo: does it need more definition?
)
class ProfileField(serializers.JSONField):
    pass
