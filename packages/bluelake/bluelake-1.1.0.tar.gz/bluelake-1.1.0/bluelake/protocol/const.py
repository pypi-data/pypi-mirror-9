# coding=utf8


CURRENT_VERSION = 1
DEFAULT_FORMAT = "JSON"

TYPE_SYNC_REQUEST = 1
TYPE_SYNC_RESPONSE = 2


JSON_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",

    # "Connection": "keepalive",
    # "Keep-Alive": 10,
}


# HTTP Response code
RESPONSE_CODE_OK = 200  # 正常返回，data内容为返回值

# RESPONSE_CODE_OK_NULL = 200.0  # 正常返回null，data可忽略

RESPONSE_OKS = (RESPONSE_CODE_OK, )

RESPONSE_CODE_BAD_REQUEST = "400"  # 客户端发出了错误的请求，客户端将抛出BadRequestException

RESPONSE_CODE_SERVICE_NOT_FOUND = "404"  # 客户端请求的服务无法找到，
                                         # 客户端将跑出ServiceNotFoundException

RESPONSE_CODE_SERVICE_ERROR = "500"  # 服务端处理请求时，抛出了一个服务异常，此异常是
                                     # 接口约定的一种场景，不是未知异常。 客户端将
                                     # 重新拼装这个异常，并抛出去。

RESPONSE_CODE_SYSTEM_ERROR = "503"  # 服务器处理请求时，遇到了意外的情况，抛出了
                                    # 不在接口约定范围内的异常。 由于并非接口约定，
                                    # 该异常的类型可能无法在客户端复现。
                                    # 客户端将统一重组一个SystemException抛出去。

