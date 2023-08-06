# -*- coding: utf-8 -*-

import datetime
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

    def to_json(self, python_obj):
        return python_obj

    def to_python(self, json_obj):
        return json_obj

    def get_default(self):
        if callable(self.default):
            return self.default()

        return copy.deepcopy(self.default)


class Field(BaseField):
    """
    默认用这个就够了
    """
    pass


class DateTimeField(BaseField):
    """
    datetime
    """
    format = '%Y-%m-%d %H:%M:%S.%f'

    def validate(self, value):
        super(DateTimeField, self).validate(value)

        if value is None:
            return

        expect_type = datetime.datetime
        assert isinstance(value, expect_type), 'type should be %s' % expect_type

    def to_json(self, python_obj):
        if python_obj is None:
            return python_obj

        return python_obj.strftime(self.format)

    def to_python(self, json_obj):
        if json_obj is None:
            return json_obj

        return datetime.datetime.strptime(json_obj, self.format)


class DateField(BaseField):
    """
    date
    """
    format = '%Y-%m-%d'

    def validate(self, value):
        super(DateField, self).validate(value)

        if value is None:
            return

        expect_type = datetime.date
        assert isinstance(value, expect_type), 'type should be %s' % expect_type

    def to_json(self, python_obj):
        if python_obj is None:
            return python_obj

        return python_obj.strftime(self.format)

    def to_python(self, json_obj):
        if json_obj is None:
            return json_obj

        return datetime.datetime.strptime(json_obj, self.format).date()


class TimeField(BaseField):
    """
    time
    """
    format = '%H:%M:%S.%f'

    def validate(self, value):
        super(TimeField, self).validate(value)

        if value is None:
            return

        expect_type = datetime.time
        assert isinstance(value, expect_type), 'type should be %s' % expect_type

    def to_json(self, python_obj):
        if python_obj is None:
            return python_obj

        return python_obj.strftime(self.format)

    def to_python(self, json_obj):
        if json_obj is None:
            return json_obj

        return datetime.datetime.strptime(json_obj, self.format).time()
