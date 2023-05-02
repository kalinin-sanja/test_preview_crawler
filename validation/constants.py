from enum import IntEnum, unique


@unique
class ServiceHTTPCodes(IntEnum):
    OK = 200
    BAD_REQUEST = 400
    UNPROCESSABLE_ENTITY = 422
    SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
