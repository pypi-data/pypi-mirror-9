#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2011-6-16
author: huwei
"""
import functools
import re


"""校验类型
"""
REQUIRED = 'required'
"""必输入项校验.
::
    validators=Validators()
    validators.rules=dict(
        name={REQUIRED:True, MAXLENGTH:40})
    validators.messages=dict(
        name={REQUIRED:'作品名称不能为空', MAXLENGTH:'作品名称不能超过40个字符'})
    if not validators.validates(shot):
        print validators.validationErrors
"""
CUSTOM = 'custom'
"""自定义校验"""
EMAIL = 'email'
"""Email校验"""
URL = 'url'
"""url校验"""
DATE = 'date'
"""日期校验"""
DATEISO = 'dateISO'
"""日期校验, 目前和date是一样的校验规则"""
NUMBER = 'number'
"""数字校验"""
DIGITS = 'digits'
"""整数校验"""
CREDITCARD = 'creditcard'
EQUALTO = 'equalTo'
"""相同值校验"""
ACCEPT = 'accept'
"""合法后缀名的字符串"""
MAXLENGTH = 'maxlength'
"""字符最大长度校验.
::
    validators=Validators()
    validators.rules=dict(
        name={REQUIRED:True, MAXLENGTH:40})
    validators.messages=dict(
        name={REQUIRED:'作品名称不能为空', MAXLENGTH:'作品名称不能超过40个字符'})
    if not validators.validates(shot):
        print validators.validationErrors
"""
MINLENGTH = 'minlength'
"""字符最小长度校验.
::
    validators=Validators()
    validators.rules=dict(
        name={MINLENGTH:2, MAXLENGTH:40})
    validators.messages=dict(
        name={MINLENGTH:'作品名称不能少于2个字符', MAXLENGTH:'作品名称不能超过40个字符'})
    if not validators.validates(shot):
        render_params['validationErrors']=validators.validationErrors
        self.render("shots/edit.html", **render_params)
        return
"""
RANGELENGTH = 'rangelength'
"""输入一个区间字符串
   RANGELENGTH => array(3,8)
::
    validators=Validators()
    validators.rules=dict(
        name={RANGELENGTH:array(2,40))
    validators.messages=dict(
        name={RANGELENGTH:'作品名称不能少于2个字符,且不超过40个字符'})
    if not validators.validates(shot):
        print validators.validationErrors
"""
RANGE = 'range'
"""区间值校验"""
MAX = 'max'
"""最大校验"""
MIN = 'min'
"""最小校验"""
ALPHABET_DIGITS = 'alphabet_digits'
"""英文字母及数字的组合"""


class Validators(object):
    """校验者类
    """
    #not empty
    VALID_NOT_EMPTY = '.+'
    #number
    VALID_NUMBER = '^[-+]?\d*\\.?\d*$'
    #A valid email address.
    VALID_EMAIL = '^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'

    VALID_URL = '''^(http(s)?://([a-zA-Z0-9]+.)(\S*?\.\S*?))(\s|\|\)|\]|\[|\{|\}|,|\"|\'|:|\<||\.\s)$'''
    VALID_DATEISO = '^\d{4}[\/-]\d{1,2}[\/-]\d{1,2}$'
    VALID_DIGITS = '^\d+$'
    #A valid year (1000-2999).
    VALID_YEAR = '^[12][0-9]{3}$'
    VALID_ALPHABET_DIGITS = '^[0-9a-zA-Z]*[a-zA-Z]+[0-9a-zA-Z]*$'

    #Returns default messages.

    DEFAULT_MESSAGES = {
        'required': u"必选字段",
        'remote': u"请修正该字段",
        'email': u"请输入正确格式的电子邮件",
        'url': u"请输入合法的网址",
        'date': u"请输入合法的日期",
        'dateISO': u"请输入合法的日期 (ISO).",
        'number': u"请输入合法的数字",
        'digits': u"只能输入整数",
        'creditcard': u"请输入合法的信用卡号",
        'equalTo': u"请再次输入相同的值",
        'accept': u"请输入拥有合法后缀名的字符串",
        'maxlength': u"请输入一个长度最多是 {0} 的字符串",
        'minlength': u"请输入一个长度最少是 {0} 的字符串",
        'rangelength': u"请输入一个长度介于 {0} 和 {1} 之间的字符串",
        'range': u"请输入一个介于 {0} 和 {1} 之间的值",
        'max': u"请输入一个最大为 {0} 的值",
        'min': u"请输入一个最小为 {0} 的值"}

    def __init__(self):
        """
        Constructor
        """
        self.rules = {}
        self.messages = {}
        self.errors = {}

    def invalidate(self, field, validate_type):
        """Sets a field as invalid.

        :param field: string field The name of the field to invalidate
        :param validate_type: validate type
        :return: void
        """
        if self.messages.get(field) and self.messages.get(field).get(validate_type):
            self.errors[field] = self.messages.get(field).get(validate_type)
        else:
            self.errors[field] = Validators.DEFAULT_MESSAGES[validate_type]

    def validates(self, data=None):
        """执行验证.
        ::
            validators=Validators()
            #设置验证规则
            validators.rules=dict(
                name={REQUIRED:True, MAXLENGTH:40})
            #设置验证失败的文案
            validators.messages=dict(
                name={REQUIRED:'作品名称不能为空', MAXLENGTH:'作品名称不能超过40个字符'})
            #执行验证
            if not validators.validates(shot):
                print validators.validationErrors
        :param data: 需要验证的数据
        :return: 验证通过返回True，否则返回False
        """
        if data is None:
            data = []
        return len(self.invalid_fields(data)) == 0
    
    def invalid_fields(self, data=None):
        """Returns an array of invalid fields.

        :param data:
        :return: return array Array of invalid fields or boolean case any error occurs
        """
        self.errors = {}
        if data is None:
            data = []
        if len(self.rules) == 0 or len(data) == 0:
            return self.errors
        for field_name, validator in self.rules.iteritems():
            for validate_type, validate_value in validator.iteritems():
                if validate_type == REQUIRED:
                    self.required_validator(field_name,
                                            data[field_name] if data.get(field_name) else None, validate_value)
                if data.get(field_name):
                    if validate_type == EMAIL:
                        self.email_validator(field_name, data[field_name], validate_value)
                    elif validate_type == ALPHABET_DIGITS:
                        self.alphabet_digits_validator(field_name, data[field_name], validate_value)
                    elif validate_type == URL:
                        self.url_validator(field_name, data[field_name], validate_value)
                    elif validate_type == DATEISO or validate_type == DATE:
                        self.dateiso_validator(field_name, data[field_name], validate_value)
                    elif validate_type == NUMBER:
                        self.number_validator(field_name, data[field_name], validate_value)
                    elif validate_type == DIGITS:
                        self.digits_validator(field_name, data[field_name], validate_value)
                    elif validate_type == CREDITCARD:
                        pass
                        # self.creditcardValidator(field_name, data[field_name], validate_value)
                    elif validate_type == EQUALTO:
                        self.equalto_validator(field_name, data[field_name], validate_value)
                    elif validate_type == MAXLENGTH:
                        self.maxlength_validator(field_name, data[field_name], validate_value)
                    elif validate_type == MINLENGTH:
                        self.minlength_validator(field_name, data[field_name], validate_value)
                    elif validate_type == RANGELENGTH:
                        self.rangelength_validator(field_name, data[field_name], validate_value)
                    elif validate_type == RANGE:
                        self.range_validator(field_name, data[field_name], validate_value)
                    elif validate_type == MAX:
                        self.max_validator(field_name, data[field_name], validate_value)
                    elif validate_type == MIN:
                        self.min_validator(field_name, data[field_name], validate_value)
                    elif validate_type == CUSTOM:
                        self.custom_validator(field_name, data[field_name], validate_value)
        return self.errors
    
    def required_validator(self, field_name, field_value, validate_value):
        if validate_value and \
                (field_value is None or (None == re.compile(Validators.VALID_NOT_EMPTY).search(field_value))):
            self.invalidate(field_name, REQUIRED)

    def custom_validator(self, field_name, field_value, validate_value):
        if field_value and (not validate_value):
            self.invalidate(field_name, CUSTOM)

    def email_validator(self, field_name, field_value, validate_value):
        if field_value and validate_value and (None == re.search(Validators.VALID_EMAIL, field_value)):
            self.invalidate(field_name, EMAIL)
    
    def alphabet_digits_validator(self, field_name, field_value, validate_value):
        if field_value and validate_value and (None == re.search(Validators.VALID_ALPHABET_DIGITS, field_value)):
            self.invalidate(field_name, ALPHABET_DIGITS)
    
    def number_validator(self, field_name, field_value, validate_value):
        if field_value and validate_value and (None == re.search(Validators.VALID_NUMBER, field_value)):
            self.invalidate(field_name, NUMBER)

    def url_validator(self, field_name, field_value, validate_value):
        if field_value and validate_value and (None == re.search(Validators.VALID_URL, field_value)):
            self.invalidate(field_name, URL)

    def dateiso_validator(self, field_name, field_value, validate_value):
        if field_value and validate_value and (None == re.search(Validators.VALID_DATEISO, field_value)):
            self.invalidate(field_name, DATEISO)

    def digits_validator(self, field_name, field_value, validate_value):
        if field_value and validate_value and (None == re.search(Validators.VALID_DIGITS, field_value)):
            self.invalidate(field_name, DIGITS)

    def equalto_validator(self, field_name, field_value, validate_value):
        if field_value != validate_value:
            self.invalidate(field_name, EQUALTO)

    def maxlength_validator(self, field_name, field_value, validate_value):
        if field_value and len(field_value) > validate_value:
            self.invalidate(field_name, MAXLENGTH)

    def minlength_validator(self, field_name, field_value, validate_value):
        if field_value and len(field_value) < validate_value:
            self.invalidate(field_name, MINLENGTH)

    def rangelength_validator(self, field_name, field_value, validate_value):
        if field_value and (len(field_value) < int(validate_value[0]) or len(field_value) > int(validate_value[1])):
            self.invalidate(field_name, RANGELENGTH)

    def range_validator(self, field_name, field_value, validate_value):
        if field_value and (int(field_value) < int(validate_value[0]) or int(field_value) > int(validate_value[1])):
            self.invalidate(field_name, RANGE)

    def max_validator(self, field_name, field_value, validate_value):
        if field_value is not None and int(field_value) > int(validate_value):
            self.invalidate(field_name, MAX)

    def min_validator(self, field_name, field_value, validate_value):
        if field_value is not None and int(field_value) < int(validate_value):
            self.invalidate(field_name, MIN)

