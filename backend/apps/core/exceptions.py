from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {'code': 500, 'message': '服务器内部错误', 'data': None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    message = '请求失败'
    errors = None

    if isinstance(response.data, dict):
        if 'detail' in response.data:
            message = str(response.data['detail'])
        else:
            errors = [
                {'field': field, 'message': str(msg[0]) if isinstance(msg, list) else str(msg)}
                for field, msg in response.data.items()
            ]
            message = errors[0]['message'] if errors else message

    return Response(
        {'code': response.status_code, 'message': message, 'errors': errors, 'data': None},
        status=response.status_code,
    )
