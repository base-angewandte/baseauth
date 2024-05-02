from rest_framework import serializers


class AutocompleteSingleTypeSerializer(serializers.Serializer):
    id = serializers.CharField()
    source = serializers.CharField(required=False)
    label = serializers.CharField()
