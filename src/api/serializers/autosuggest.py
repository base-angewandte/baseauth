from rest_framework.fields import CharField
from rest_framework.serializers import Serializer


class AutosuggestUserSerializer(Serializer):
    UUID = CharField()
    first_name = CharField()
    last_name = CharField()
    label = CharField()


class AutosuggestFieldLabelSerializer(Serializer):
    de = CharField()
    en = CharField()


class AutosuggestFieldSerializer(Serializer):
    source = CharField()
    label = AutosuggestFieldLabelSerializer()
    source_name = CharField()
