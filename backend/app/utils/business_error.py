from rest_framework.exceptions import APIException


class BusinessError(APIException):
    """业务异常：携带明确的错误码与中文提示，交由统一异常处理返回标准格式。"""

    def __init__(self, message: str, err_code: str = 'BUSINESS_ERROR', http_status: int = 400):
        self.err_code = err_code
        self.status_code = http_status
        self.detail = message
        super().__init__(detail=message)
