# coding=utf8
import re
import json
import logging
from bluelake.client.sender import sender_dict

from .exc import *
from ..protocol.const import *
from ..protocol.request import BLRequest
from ..protocol.response import BLResponse


URL_FORMAT = r'(http://|https://).+:\d{1,5}'
DEFAULT_TIMEOUT = 10  # seconds

logging.getLogger("requests").setLevel(logging.WARNING)


def rpc(url, service, method, arg_map, sender=None):
    """ Do RPC

    :param url: remote host and port, e.g. "localhost:8080"
    :param service: remote service name
    :param method: remote method name
    :param arg_map: arg_map in key-value pairs
    :return: remote rpc result
    """
    # check url
    url = _check_url(url)

    # create request
    bl_request = BLRequest(service, method, arg_map)

    # do rpc
    bl_response = _send_request(url, bl_request, sender=sender)

    # check requestId
    if bl_response.requestId != bl_request.requestId:
        raise BLDiffRequestIdError()

    # check response code
    if int(bl_response.get_code()) not in RESPONSE_OKS:
        exc_type = str(bl_response.get_data().get('_type', ''))
        message = bl_response.get_data().get('_message', '')
        raise type(exc_type, (BluelakeError, ), {})(message=message)

    return bl_response.get_data()


def _send_request(url, bl_request, headers=None, sender='requests'):
    sender_method = sender_dict.get(sender, None)
    if not sender_method:
        raise SenderNotValidError()
    content, status = sender_method(url,
                                  data=bl_request.to_json(),
                                  headers=headers or JSON_HEADERS,
                                  timeout=DEFAULT_TIMEOUT)

    return _parse_response(content)


def _parse_response(content):
    res_content = json.loads(content)
    bl_content = json.loads(res_content['content'])
    code = bl_content['code']
    data = json.loads(bl_content['data'])
    return BLResponse(res_content['requestId'], data, code)


def _check_url(url):
    """

    :param url: should be something like 'http://192.168.1.213:8809'
                                             or '192.168.1.213:8809'
    :return: True or raise exception
    """
    if not isinstance(url, str):
        raise URLInvalidError('<url> should be string type.')

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    match = re.match(URL_FORMAT, url)
    if not match:
        raise URLInvalidError('Bad format for <url>.')

    return url
