# -*- coding: utf-8 -*-

import json


# 被定义过的models
defined_models = dict()


def custom_dumps(python_object):
    if isinstance(python_object, tuple(defined_models.values())):
        return python_object.to_json()

    # print python_object
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def custom_loads(json_object):
    if '__class__' in json_object:
        obj = defined_models[json_object['__class__']]()
        obj.from_json(json_object)
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


def register_models(models):
    defined_models.update(
        dict([(model.__name__, model) for model in models])
    )