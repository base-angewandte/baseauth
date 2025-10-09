from http import HTTPStatus

from rest_framework import status
from rest_framework.renderers import JSONRenderer

from django.conf import settings
from django.urls import resolve
from django.utils.functional import lazy
from django.utils.translation import get_language

from .pagination import EnvelopePagination

get_language_lazy = lazy(get_language, str)

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
        request = renderer_context.get('request')
        view = renderer_context.get('view')
        project_name = settings.ROOT_URLCONF.split('.')[0]
        resolver_match = resolve(request.path_info)
        endpoint_name = resolver_match.url_name

        # Skip renderer, if the api isn't v2 (for portfolio and baseauth)
        if (
            (project_name == 'baseauth' or project_name == 'portfolio')
            and (request.version != 'v2')
            or getattr(view, 'skip_envelope', False)
        ):
            return super().render(data, accepted_media_type, renderer_context)

        # Skip renderer, if the data is already present in the response
        if (
            isinstance(data, dict)
            and {'status', 'code', 'msg', 'meta', 'data'} <= data.keys()
        ):
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context['response']

        # Skip renderer for binary/streaming responses
        if getattr(response, 'streaming', False):
            return super().render(data, accepted_media_type, renderer_context)
        # As Portfolio's is using Python 3.9, the newer style unions (X | Y) can't be used for it.
        # That's why I decided that for image and baseauth the older union style will be used,
        # if we don't decide otherwise.
        if not isinstance(data, (dict, list, tuple)):  # noqa UP038
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code

        if getattr(view, 'skip_envelope', False):
            return super().render(data, accepted_media_type, renderer_context)

        # Build meta
        meta = {}
        is_success = status.is_success(status_code)
        wrapper = {
            'status': SUCCESS_KEY if is_success else FAILURE_KEY,
            'code': status_code,
        }
        view_module = getattr(view, '__module__', '')
        excluded = getattr(settings, 'EXCLUDE_LANGUAGES_FROM_URLS', ())

        is_excluded = any(
            view_module == p or view_module.startswith(p + '.') for p in excluded
        )

        if not is_excluded:
            meta['language'] = get_language_lazy()

        # Early exit because of pagination (Portfolio API /entry):
        if (
            project_name == 'portfolio'
            and isinstance(response.data, dict)
            and {'total', 'offset', 'limit', 'result_count', 'data'}
            <= response.data.keys()
        ):
            meta = {
                'limit': response.data['limit'],
                'offset': response.data['offset'],
                'total': response.data['total'],
                'result_count': response.data['result_count'],
            }
            payload = response.data['data']
            wrapper['meta'] = meta
            wrapper['data'] = payload
            return super().render(wrapper, accepted_media_type, renderer_context)

        qp = request.query_params

        limit_raw = qp.get('limit')
        offset_raw = qp.get('offset')

        if (
            (('limit' in qp) or ('offset' in qp))
            and isinstance(response.data, dict)
            and 'results' in response.data
        ):
            limit = None
            offset = None

            if limit_raw is not None:
                limit = int(limit_raw)
            if offset_raw is not None:
                offset = int(offset_raw)

            meta = {
                'limit': limit,
                'offset': offset,
                'total': response.data.get('total')
                or response.data.get('count')
                or len(response.data['results']),
                'result_count': response.data.get('result_count')
                or len(response.data['results']),
            }
        # (image) -permissions workaround
        elif (
            ('limit' in qp)
            or ('offset' in qp)
            and project_name == 'image'
            and endpoint_name == 'permission-list'
            and isinstance(response.data, list)
            and is_success
        ):
            paginator = EnvelopePagination()
            paged = paginator.paginate_queryset(response.data, request)
            meta_raw = paginator.get_paginated_response(list(paged)).data
            meta = {
                'limit': meta_raw['limit'],
                'offset': meta_raw['offset'],
                'total': meta_raw['total'],
                'result_count': meta_raw['result_count'],
            }
            payload = meta_raw['data']

            default_msg = HTTPStatus(status_code).phrase or 'Successful Transaction'
            wrapper['msg'] = renderer_context.get('msg', default_msg)
            wrapper['meta'] = meta
            wrapper['data'] = payload
            return super().render(wrapper, accepted_media_type, renderer_context)

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
                        key: (val[0] if isinstance(val, (list, tuple)) and val else val)  # noqa UP038
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
                    if isinstance(error_message, (list, tuple)):  # noqa UP038
                        errors.extend(error_message)
                    elif error_message:
                        errors.append(error_message)
            elif isinstance(payload, (list, tuple)):  # noqa UP038
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
