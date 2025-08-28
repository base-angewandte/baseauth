from http import HTTPStatus

from rest_framework import status
from rest_framework.renderers import JSONRenderer

SUCCESS_KEY = 'success'
FAILURE_KEY = 'failure'


class ApiRenderer(JSONRenderer):
    """
    Wrap every response in the standard body:
        {
          "status": "success" | "failure",
          "code": 200,
          "msg": "Successful Transaction" | "Validation Error" | ...,
          "meta": {...}?,   # injected by pagination class
          "data": object | list | null
        }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Skip renderer, if the data is already present in the response
        if (
            isinstance(data, dict)
            and {'status', 'code', 'msg', 'meta', 'data'} <= data.keys()
        ):
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context['response']

        # skip binary/streaming responses
        if getattr(response, 'streaming', False):
            return super().render(data, accepted_media_type, renderer_context)
        if not isinstance(data, dict | list | tuple):
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code
        request = renderer_context.get('request')
        view = renderer_context.get('view')

        # Skip api v1 and completely exempt endpoints from renderer
        if request.version != 'v2' or getattr(view, 'skip_envelope', False):
            return super().render(data, accepted_media_type, renderer_context)

        is_success = status.is_success(status_code)

        wrapper = {
            'status': SUCCESS_KEY if is_success else FAILURE_KEY,
            'code': status_code,
        }

        # Build meta
        meta = {}
        if (
            getattr(view, 'accept_language_header', False)
            and 'HTTP_ACCEPT_LANGUAGE' in request.META
        ):
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
            if isinstance(payload, dict) and status_code == 400:
                if 'detail' in payload:
                    wrapper['msg'] = str(payload.get('detail')) or default_msg
                    wrapper['data'] = None
                    return super().render(
                        wrapper,
                        accepted_media_type,
                        renderer_context,
                    )
                if any(k != 'detail' for k in payload):
                    normalized = {
                        key: (val[0] if isinstance(val, list | tuple) and val else val)
                        for key, val in payload.items()
                    }
                    wrapper['data'] = normalized
                    return super().render(
                        wrapper,
                        accepted_media_type,
                        renderer_context,
                    )

            errors = []
            if isinstance(payload, dict):
                for error_message in payload.values():
                    if isinstance(error_message, list | tuple):
                        errors.extend(error_message)
                    elif error_message:
                        errors.append(error_message)
            elif isinstance(payload, list | tuple):
                errors = list(payload)
            elif isinstance(payload, str):
                errors = [payload]

            if not errors:
                wrapper['data'] = payload
            elif len(errors) == 1:
                wrapper['data'] = errors[0]
            else:
                wrapper['data'] = errors

        return super().render(wrapper, accepted_media_type, renderer_context)
