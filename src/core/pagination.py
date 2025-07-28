from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class EnvelopePagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(
            {
                'total': self.count,
                'offset': self.offset,
                'limit': self.limit,
                'result_count': len(data),
                'results': data,
            },
        )
