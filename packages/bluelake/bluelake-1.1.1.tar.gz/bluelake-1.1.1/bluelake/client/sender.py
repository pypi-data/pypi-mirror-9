# coding=utf8
import httplib
import requests
from .exc import *


def do_requests(url, data, headers, timeout):
    try:
        response = requests.post(url,
                             data=data,
                             headers=headers,
                             timeout=timeout)
        return response.content, response.status_code
    except requests.ConnectionError:
        raise ConnectionError()
    except requests.HTTPError:
        raise ConnectionError()
    except requests.Timeout:
        raise ConnectionError('Connect timeout.')


def do_httplib(url, data, headers, timeout):
    host, port, path = _parse_url(url)
    conn = None
    try:
        conn = httplib.HTTPConnection(host, port=port, timeout=timeout)
        conn.request('POST', path, body=data, headers=headers)
        response = conn.getresponse()
        return response.read(), response.status
    except:
        raise ConnectionError()
    finally:
        if conn:
            conn.close()


def _parse_url(url):
    if url.startswith('http://'):
        url = url[7:]

    host, port_path = url.split(':', 1)
    port_path_list = port_path.split('/', 1)
    port = port_path_list[0]
    path = port_path_list[1] if len(port_path_list) == 2 else ''

    if not host or not port:
        raise URLInvalidError()

    try:
        port = int(port)
    except ValueError:
        raise URLInvalidError()

    return host, port, path


sender_dict = {
    'requests': do_requests,
    'httplib': do_httplib,
}
