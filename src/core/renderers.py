from http import HTTPStatus

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

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

    media_type = 'application/json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context['response']
        status_code = response.status_code
        view_context = renderer_context.get('view')
        if getattr(view_context, 'skip_envelope', False):
            return super().render(data, accepted_media_type, renderer_context)

        is_success = status.is_success(status_code)

        if isinstance(data, ReturnDict | ReturnList):
            data = dict(data) if isinstance(data, ReturnDict) else list(data)

        wrapper = {
            'status': SUCCESS_KEY if is_success else FAILURE_KEY,
            'code': status_code,
        }
        pagination = getattr(response, 'pagination', None)
        if is_success:
            default_msg = HTTPStatus(status_code).phrase or 'Successful Transaction'
            wrapper['msg'] = renderer_context.get('msg', default_msg)
            wrapper['data'] = data
            if pagination is not None:
                wrapper['pagination'] = pagination
        else:
            default_msg = HTTPStatus(status_code).phrase
            wrapper['msg'] = default_msg if status_code != 400 else 'Validation Error'
            wrapper['data'] = data

        return super().render(wrapper, accepted_media_type, renderer_context)
