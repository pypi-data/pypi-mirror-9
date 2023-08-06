# -*- coding: utf-8 -*-

import copy


class BaseField(object):
    default = None
    null = None

    def __init__(self, default=None, null=False):
        self.default = default
        self.null = null

    def validate(self, value):
        if not self.null and value is None:
            raise ValueError('should not be None')

    def get_default(self):
        if callable(self.default):
            return self.default()

        return copy.deepcopy(self.default)


class Field(BaseField):
    """
    默认用这个就够了
    """
    pass