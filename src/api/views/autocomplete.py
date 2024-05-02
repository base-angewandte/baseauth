import json

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from django.db import models

from api.serializers.autocomplete import AutocompleteSingleTypeSerializer


class AutocompleteView(APIView):
    AUTOCOMPLETE_DEFAULT_LIMIT = 10

    def parse_query_params(self, request):
        q = request.query_params.get('q', None)
        if not q:
            raise serializers.ValidationError('Query parameter "q" is required')

        autocomplete_type = request.query_params.get('type', None)
        if not autocomplete_type:
            raise serializers.ValidationError('Query parameter "type" is required')

        limit = request.query_params.get('limit', None)
        if not limit:
            limit = self.AUTOCOMPLETE_DEFAULT_LIMIT
        try:
            limit = int(limit)
        except ValueError:
            raise serializers.ValidationError(
                'Query parameter "limit" must be an integer'
            )

        return q, autocomplete_type, limit

    def check_autocomplete_type_is_valid(self, autocomplete_type: str):
        """
        Checks if autocomplete type is valid.
        NOTE Currently only 'users' are supported.
        """

        if autocomplete_type.lower().strip() != "users":
            raise serializers.ValidationError(
                'Query parameter "type" expected to be "users"'
            )

    @extend_schema(
        tags=["autocomplete"],
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                description="Query string",
                required=True,
            ),
            OpenApiParameter(
                name="type",
                type=str,
                description="Type of autocomplete",
                required=True,
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                description="Limit of results",
                required=False,
            ),
        ],
        responses={
            200: OpenApiResponse(response=AutocompleteSingleTypeSerializer(many=True)),
            400: OpenApiResponse("Bad request"),
        },
    )
    def get(self, request, *args, **kwargs):
        q, autocomplete_type, limit = self.parse_query_params(request)
        self.check_autocomplete_type_is_valid(autocomplete_type)

        UserModel = get_user_model()
        filtered_users = UserModel.objects.annotate(
            full_name=models.Concat(
                models.F("first_name"), models.Value(" "), models.F("last_name")
            )
        )
        for query_part in q.split():
            # filter by parts of query - this allows partial matching of either first or last name
            filtered_users = filtered_users.filter(
                models.Q(full_name__icontains=query_part)
            )

        serializer = AutocompleteSingleTypeSerializer(filtered_users[:limit], many=True)
        return Response(serializer.data)
