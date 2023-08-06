# -*- coding: utf-8 -*-

import json

# 被定义过的models
defined_models = dict()


def custom_dumps(python_object):
    if python_object.__class__.__name__ in defined_models:
        model = defined_models[python_object.__class__.__name__]

        if isinstance(model, dict):
            return model['to_json'](python_object)
        else:
            return python_object.to_json()

    # print python_object
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def custom_loads(json_object):
    if '__class__' in json_object:
        model = defined_models.get(json_object['__class__'])
        if model is not None:
            if isinstance(model, dict):
                return model['from_json'](json_object)
            else:
                obj = model()
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
    """
    注册models
    :param models:
        model可以为两种类型:
            1. 自定义类，比如Desk，这种可以自己内部实现to_json 和 from_json 的。
            2. 内置类，比如datetime，这种我们没法修改其内部。
                {
                    'type': datetime,
                    'to_json': xxx,
                    'from_json': yyy,
                }
        :return:
    """
    defined_models.update(
        dict([(model['type'].__name__ if isinstance(model, dict) else model.__name__, model) for model in models])
    )