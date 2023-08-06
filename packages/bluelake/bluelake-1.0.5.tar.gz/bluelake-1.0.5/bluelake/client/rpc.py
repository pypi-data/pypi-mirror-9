# coding=utf8
import re
import requests
from bluelake.exc import URLInvalidExc

from ..model import *

URL_FORMAT = r'(http://|https://).+:\d{1,5}'


def rpc(url, service, method, arg_map):
    """ Do RPC

    :param url: remote host and port, e.g. "localhost:8080"
    :param service: remote service name
    :param method: remote method name
    :param arg_map: arg_map in key-value pairs
    :return: remote rpc result
    """
    # check url
    check_url(url)

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


def check_url(url):
    """

    :param url: should be something like 'http://192.168.1.213:8809'
                                             or '192.168.1.213:8809'
    :return: True or raise exception
    """
    if not isinstance(url, str):
        raise URLInvalidExc('<url> should be string type.')

    if not url.startswith('http://') or not url.startswith('https://'):
        url = 'http://' + url

    match = re.match(URL_FORMAT, url)
    if not match:
        raise URLInvalidExc('Bad format for <url>.')

    return True
