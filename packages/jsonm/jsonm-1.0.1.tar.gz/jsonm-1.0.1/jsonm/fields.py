# -*- coding: utf-8 -*-

import copy


class BaseField(object):
    default = None
    null = None

    def __init__(self, default=None, null=False):
        self.default = copy.deepcopy(default)
        self.null = null


class Field(BaseField):
    """
    默认用这个就够了
    """
    pass