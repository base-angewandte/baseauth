import json

import jsonschema
from jsonschema import validate
from rest_framework import serializers
from rest_framework.fields import empty

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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


class CleanModelSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = self.Meta.model(**attrs)
        instance.clean()
        return attrs


class SwaggerMetaModelSerializer(serializers.ModelSerializer):
    @staticmethod
    def _swagger_meta(attrs=None):
        class Meta:
            swagger_schema_fields = {'x-attrs': attrs} if attrs else None

        return Meta

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'swagger_meta_attrs'):
            for f, attrs in self.Meta.swagger_meta_attrs.items():
                field = self.fields.get(f)
                if field and attrs:
                    if hasattr(field, 'Meta'):
                        # TODO needs changes`? was update()
                        field.Meta.swagger_schema_fields.update({'x-attrs': attrs})
                    else:
                        field.Meta = self._swagger_meta(attrs=attrs)
