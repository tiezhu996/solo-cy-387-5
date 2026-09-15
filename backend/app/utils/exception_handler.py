from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from app.utils.business_error import BusinessError
from app.utils.logger import get_logger

logger = get_logger('exception')


def standard_exception_handler(exc, context):
    """统一异常处理：所有异常都返回 {success, code, message, data} 标准格式。"""
    # 业务异常：携带明确错误码与提示
    if isinstance(exc, BusinessError):
        logger.info('业务异常 [%s] %s', exc.err_code, exc.detail)
        return Response(
            {'success': False, 'code': exc.err_code, 'message': str(exc.detail), 'data': None},
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        logger.exception('未处理异常')
        return Response(
            {'success': False, 'code': 'INTERNAL_ERROR', 'message': '服务器内部错误', 'data': None},
            status=500,
        )

    # 规整 DRF 自带异常（404 / 405 / 字段校验等）
    detail = response.data
    if isinstance(detail, dict) and 'detail' in detail:
        message = str(detail['detail'])
    elif isinstance(detail, dict):
        # 字段校验错误：取出第一个字段的第一条提示
        first = next(iter(detail.values()), None)
        if isinstance(first, (list, tuple)) and first:
            first = first[0]
        message = str(first) if first else '请求参数有误'
    else:
        message = '请求参数有误'
    return Response(
        {'success': False, 'code': 'REQUEST_ERROR', 'message': message, 'data': None},
        status=response.status_code,
    )
