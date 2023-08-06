#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import functools
from app.commons.validators import Validators
from app.commons.view_model import ViewModel

__author__ = 'freeway'


def validators(rules=None, messages=None):
    """validators decorater
    just for tornado
    会给self.对象加入
    :param rules: 校验规则
    :param messages: 出错信息

    """
    def _validators(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if rules is None or len(rules) == 0:
                return method(self, *args, **kwargs)
            validate = Validators()
            #设置验证规则
            validate.rules = copy.deepcopy(rules)
            #设置验证失败的文案
            if messages is not None:
                validate.messages = messages
            valid_data = ViewModel()
            for field_name, validator in validate.rules.iteritems():
                valid_data[field_name] = self.get_argument(field_name, '')
                for validate_type, validate_value in validator.iteritems():
                    if isinstance(validate_value, str) or isinstance(validate_value, unicode):
                        if '#' == validate_value[:1]:
                            validator[validate_type] = self.get_argument(validate_value[1:], '')
            self.validation_success = validate.validates(valid_data)
            self.validation_errors = validate.errors
            self.validation_data = valid_data

            return method(self, *args, **kwargs)
        return wrapper
    return _validators
