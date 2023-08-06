# coding=utf8
import json

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
