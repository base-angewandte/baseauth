import json

from apimapper import APIMapper
from rest_framework.utils.encoders import JSONEncoder

from django.conf import settings


def fetch_responses(querystring, active_sources):
    responses = []
    for src in active_sources:
        api = APIMapper(
            # this is kinda hacky - change it if there's a better solution to force evaluation of lazy objects
            # inside a dict
            json.loads(json.dumps(settings.SOURCES.get(src), cls=JSONEncoder)),
            settings.RESPONSE_MAPS.get(src),
            timeout=2,
        )
        res = api.fetch_results(querystring)
        responses.extend(res)

    return responses
