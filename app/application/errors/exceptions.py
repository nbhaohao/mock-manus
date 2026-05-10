from typing import Any


class AppException(RuntimeError):

    def __init__(self, code: int = 400, status_code: int = 400, msg: str = '应用发生错误请稍后重试',
                 data: Any = None):
        self.code = code
        self.status_code = status_code
        self.msg = msg
        self.data = data
        super().__init__()


class BadRequestError(AppException):
    def __init__(self, msg: str = "客户端请求错误, 请检查后重试"):
        super().__init__(status_code=400, code=400, msg=msg)


class NotFoundError(AppException):
    def __init__(self, msg: str = "资源未找到"):
        super().__init__(status_code=404, code=404, msg=msg)


class ValidationError(AppException):
    def __init__(self, msg: str = "数据校验错误"):
        super().__init__(status_code=422, code=422, msg=msg)


class TooManyRequestsError(AppException):
    def __init__(self, msg: str = "请求过多"):
        super().__init__(status_code=429, code=429, msg=msg)


class ServerRequestError(AppException):
    def __init__(self, msg: str = "服务器出现异常, 请稍后重试"):
        super().__init__(status_code=500, code=500, msg=msg)
