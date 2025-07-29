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
        response = renderer_context['response']
        status_code = response.status_code
        view_context = renderer_context.get('view')

        request = renderer_context.get('request')
        view = renderer_context.get('view')

        if request.version != 'v2' or getattr(view, 'skip_envelope', False):
            return super().render(data, accepted_media_type, renderer_context)

        if getattr(view_context, 'skip_envelope', False):
            return super().render(data, accepted_media_type, renderer_context)

        is_success = status.is_success(status_code)

        wrapper = {
            'status': SUCCESS_KEY if is_success else FAILURE_KEY,
            'code': status_code,
        }

        pagination = None
        if isinstance(response.data, dict) and (
            {'total', 'offset', 'limit', 'result_count', 'results'}
            & response.data.keys()
        ):
            pagination = {
                'total': response.data.get('total', 0),
                'offset': response.data.get('offset', 0),
                'limit': response.data.get('limit', 0),
                'results_count': response.data.get('result_count', 0),
            }

        payload = (
            response.data['results']
            if isinstance(response.data, dict) and 'results' in response.data
            else response.data
        )

        if is_success:
            default_msg = HTTPStatus(status_code).phrase or 'Successful Transaction'
            wrapper['msg'] = renderer_context.get('msg', default_msg)
            wrapper['data'] = payload
            if pagination:
                wrapper['pagination'] = pagination
        else:
            default_msg = HTTPStatus(status_code).phrase
            wrapper['msg'] = default_msg if status_code != 400 else 'Validation Error'
            wrapper['data'] = payload

        return super().render(wrapper, accepted_media_type, renderer_context)
