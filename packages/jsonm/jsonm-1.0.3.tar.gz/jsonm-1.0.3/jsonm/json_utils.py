# -*- coding: utf-8 -*-

import json
from .model import Model


def custom_dumps(python_object):
    if isinstance(python_object, tuple(Model.model_defines.values())):
        return python_object._to_json()

    # print python_object
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def custom_loads(json_object):
    if '__class__' in json_object:
        obj = Model.model_defines[json_object['__class__']]()
        obj._from_json(json_object)
        return obj

    return json_object


def json_dumps(*args, **kwargs):
    kwargs.update(dict(
        default=custom_dumps
    ))

    return json.dumps(*args, **kwargs)


def json_loads(*args, **kwargs):
    kwargs.update(dict(
        object_hook=custom_loads
    ))

    return json.loads(*args, **kwargs)
