from collections.abc import Sized
from typing import Any

from django.conf import settings
from rest_framework.response import Response


def limited_list_response(data: Any, *, total: int, limit: int | None = None) -> Response:
    """Return a list response with explicit cap metadata in headers."""
    effective_limit = limit if limit is not None else settings.MAX_LIST_RESULTS
    response = Response(data)
    response['X-List-Limit'] = str(effective_limit)
    response['X-List-Total'] = str(total)
    response['X-List-Truncated'] = 'true' if total > _data_length(data, effective_limit) else 'false'
    return response


def _data_length(data: Any, fallback: int) -> int:
    if isinstance(data, Sized):
        return len(data)
    return fallback
