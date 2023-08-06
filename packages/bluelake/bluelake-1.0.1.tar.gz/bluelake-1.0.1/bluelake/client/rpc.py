# coding=utf8
import requests

from ..model import *


def rpc(url, service, method, arg_map):
    """ Do RPC

    :param url: remote host and port, e.g. "localhost:8080"
    :param service: remote service name
    :param method: remote method name
    :param arg_map: arg_map in key-value pairs
    :return: remote rpc result
    """
    # create request
    bl_request = BLRequest(service, method, arg_map)

    # do rpc
    bl_response = send_request(url, bl_request, None)

    # check response
    bl_response.check_code()

    return bl_response.data


def send_request(url, bl_request, headers=None):
    response = requests.post(url,
                             data=bl_request.to_json(),
                             headers=headers or JSON_HEADERS)
    return BLResponse(response)
