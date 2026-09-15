from rest_framework.response import Response


def success(data=None, message: str = 'ok', code: int = 200) -> Response:
    """统一成功响应。"""
    return Response({'success': True, 'code': code, 'message': message, 'data': data}, status=code)


def fail(message: str, code=400, data=None) -> Response:
    """统一失败响应（业务流程内主动返回时使用）。"""
    return Response({'success': False, 'code': code, 'message': message, 'data': data}, status=code)
