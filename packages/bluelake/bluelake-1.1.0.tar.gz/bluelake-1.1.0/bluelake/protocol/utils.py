# coding=utf8
import copy
import json

from .const import *

LIST_TYPES = (list, tuple, set)


def to_bluelake_json(obj):
    """ Convert Python object to bluelake Protocol JSON

    :param obj: Python Object
    :return: BLP JSON
    """
    return json.dumps(to_bluelake_obj(obj))


def to_bluelake_obj(obj):
    """ Convert Python object to bluelake Protocol object using
        python object's __dict__ attribute.

    :param obj:
    :return:
    """
    if hasattr(obj, '__dict__'):
        obj_dict = {}
        for key, value in obj.__dict__.iteritems():
            if key.startswith('__'):
                continue
            obj_dict.__setitem__(key, to_bluelake_obj(value))
        return obj_dict

    if type(obj) in LIST_TYPES:
        result_obj = []
        for o in obj:
            result_obj.append(to_bluelake_obj(o))
        return result_obj

    if isinstance(obj, dict):
        result_obj = {}
        for key, value in obj.iteritems():
            result_obj.__setitem__(key, to_bluelake_obj(value))
        return result_obj

    return obj


def parse_request(request_json):
    """ Parse request json data to dicts.

    :param request_json:
    :return:
    """
    # parse request
    rv = json.loads(request_json)
    # parse content
    content = json.loads(rv.get('content', '""'))
    arg_dict = content.get('argMap', None)
    if arg_dict:
        #parse args
        for name, value in arg_dict.iteritems():
            arg_dict.__setitem__(name, json.loads(value))
    rv.__setitem__('content', content)
    return rv


def make_json_response(result, request):
    response = copy.copy(request)
    content = {
        'code': RESPONSE_CODE_OK,
        'data': to_bluelake_json(result)
    }

    response['type'] = TYPE_SYNC_RESPONSE
    response['content'] = to_bluelake_json(content)
    return to_bluelake_json(response)


class JsonMixIn(object):
    """ Convert bluelake object to json """

    def to_json(self):
        return to_bluelake_json(self)
