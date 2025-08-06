from http import HTTPStatus

from rest_framework import status
from rest_framework.renderers import JSONRenderer

SUCCESS_KEY = 'success'
FAILURE_KEY = 'failure'


class ApiRenderer(JSONRenderer):
    """
    Wrap every response in the standard body:
        {
          "status": "Success" | "Failure",
          "code": 200,
          "msg": "Successful Transaction" | "Validation Error" | ...,
          "pagination": {...}?,   # injected by pagination class
          "data": object | list | null
        }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if (
            isinstance(data, dict)
            and {'status', 'code', 'msg', 'meta', 'data'} <= data.keys()
        ):
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context['response']
        status_code = response.status_code
        request = renderer_context.get('request')
        view = renderer_context.get('view')

        if request.version != 'v2' or getattr(view, 'skip_envelope', False):
            return super().render(data, accepted_media_type, renderer_context)

        is_success = status.is_success(status_code)

        wrapper = {
            'status': SUCCESS_KEY if is_success else FAILURE_KEY,
            'code': status_code,
        }

        meta = {}
        lang = getattr(request, 'LANGUAGE_CODE', None)
        if lang:
            meta['language'] = lang
        if isinstance(response.data, dict) and {
            'total',
            'offset',
            'limit',
            'result_count',
            'results',
        }.issubset(response.data):
            meta['pagination'] = {
                k: response.data.get(k, 0)
                for k in ('total', 'offset', 'limit', 'result_count')
            }

        payload = (
            response.data['results']
            if isinstance(response.data, dict) and 'results' in response.data
            else response.data
        )

        if is_success:
            default_msg = HTTPStatus(status_code).phrase or 'Successful Transaction'
            wrapper['msg'] = renderer_context.get('msg', default_msg)
            wrapper['meta'] = meta
            wrapper['data'] = payload

        else:
            default_msg = HTTPStatus(status_code).phrase
            wrapper['msg'] = default_msg
            wrapper['data'] = payload

        return super().render(wrapper, accepted_media_type, renderer_context)
