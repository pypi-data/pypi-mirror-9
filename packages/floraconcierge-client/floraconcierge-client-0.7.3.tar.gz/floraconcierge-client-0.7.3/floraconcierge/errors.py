class ApiError(Exception):
    def __init__(self, *args, **kwargs):
        self.result = kwargs.pop('result', None)

        super(ApiError, self).__init__(*args, **kwargs)


class HTTPError(ApiError):
    def __init__(self, base_http_error, *args, **kwargs):
        self.base_error = base_http_error

        super(HTTPError, self).__init__(*args, **kwargs)


class MalformedJSONResultError(ApiError):
    pass


class ModelMappingNotFoundError(ApiError):
    pass


class MiddlewareError(ApiError):
    pass


class ResultError(ApiError):
    pass


class ResultDefaultError(ApiError):
    pass


class ResultBadArgumentsError(ApiError):
    pass


class ResultInvalidApiIDValueError(ApiError):
    pass


class ResultInvalidSignValueError(ApiError):
    pass


class ResultApplicationNotFoundError(ApiError):
    pass


class ResultBadSignatureError(ApiError):
    pass


class ResultApiNotFoundError(ApiError):
    pass


class ResultObjectNotFoundError(ApiError):
    pass


class ResultInvalidParameterValueError(ApiError):
    pass


class ResultUserAuthorizationRequiredError(ApiError):
    pass


def get_result_error(result, error):
    errors = {
        0xffff: ResultDefaultError,
        0x01: ResultBadArgumentsError,
        0x02: ResultInvalidApiIDValueError,
        0x03: ResultInvalidSignValueError,
        0x04: ResultApplicationNotFoundError,
        0x05: ResultBadSignatureError,
        0x06: ResultApiNotFoundError,
        0x07: ResultObjectNotFoundError,
        0x08: ResultInvalidParameterValueError,
        0x10: ResultUserAuthorizationRequiredError
    }

    cls = errors.get(error.code, ResultDefaultError)

    return cls(error.message, result=result)
