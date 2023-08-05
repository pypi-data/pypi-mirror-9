# -*- coding: utf-8 -*-

from .fields import BaseField


class Model(object):

    # 类变量
    custom_classes = dict()

    # 存储的前缀
    __prefix__ = None

    def __init__(self):
        for attr, field_def in self._fields_dict().items():
            setattr(self, attr, field_def.default)

        self.__class__.custom_classes[self.__class__.__name__] = self.__class__

    def to_json(self):
        """
        导出为json
        :return:
        """
        self._validate()

        value = dict()
        for attr in self._fields_dict().keys():
            value[attr] = getattr(self, attr, None)

        return dict(
            __class__=self.__class__.__name__,
            __value__=value
        )

    def from_json(self, json_str):
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

    def _validate(self):
        """
        验证参数是否合法
        :return:
        """

        for attr, field_def in self._fields_dict().items():
            if not field_def.null and getattr(self, attr, None) is None:
                raise TypeError('%s should not be None' % attr)

    @classmethod
    def load(cls, rds, id):
        """
        从存储里读入
        :param rds:
        :param id:
        :return:
        """
        from .json_utils import json_loads

        key = '%s:%s' % (cls.__prefix__ or cls.__name__, id)

        try:
            return json_loads(rds.get(key))
        except:
            return None

    def save(self, rds):
        from .json_utils import json_dumps

        key = '%s:%s' % (self.__class__.__prefix__ or self.__class__.__name__, self.id)

        try:
            return rds.set(key, json_dumps(self))
        except:
            return None

    def __str__(self):
        from .json_utils import json_dumps

        return json_dumps(self, indent=4)
