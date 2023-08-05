# -*- coding: utf-8 -*-

from .fields import BaseField


class Model(object):

    # 存储的前缀
    __prefix__ = None

    def __init__(self):
        for attr, field_def in self._fields_dict().items():
            setattr(self, attr, field_def.default)

    def _to_json(self):
        """
        导出为json
        :return:
        """
        self.validate()

        value = dict()
        for attr in self._fields_dict().keys():
            value[attr] = getattr(self, attr, None)

        return dict(
            __class__=self.__class__.__name__,
            __value__=value
        )

    def _from_json(self, json_str):
        """
        从json解析
        :param json_str:
        :return:
        """

        json_value = json_str['__value__']

        for attr in self._fields_dict().keys():
            setattr(self, attr, json_value.get(attr))

    def _fields_dict(self):
        """
        获取fields
        :return:
        """

        fields_dict = dict()

        for attr in dir(self.__class__):
            val = getattr(self.__class__, attr)
            if isinstance(val, BaseField):
                fields_dict[attr] = val

        return fields_dict

    def validate(self):
        """
        验证参数是否合法
        :return:
        """

        for attr, field_def in self._fields_dict().items():
            if not field_def.null and getattr(self, attr, None) is None:
                raise ValueError('%s.%s should not be None' % (self.__class__.__name__, attr))

    @classmethod
    def load(cls, rds, id):
        """
        从存储里读入
        :param rds:
        :param id:
        :return:
        """
        from .utils import json_loads

        key = '%s:%s' % (cls.__prefix__ or cls.__name__, id)

        return json_loads(rds.get(key))

    def save(self, rds):
        from .utils import json_dumps

        key = '%s:%s' % (self.__class__.__prefix__ or self.__class__.__name__, self.id)

        return rds.set(key, json_dumps(self))

    def __str__(self):
        from .utils import json_dumps

        return json_dumps(self, indent=4)
