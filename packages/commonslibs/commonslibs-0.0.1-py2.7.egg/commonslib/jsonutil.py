#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
from tornado.escape import to_basestring

__author__ = 'freeway'


class JSONExtensionEncoder(json.JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime.date):
                encoded_object = obj.strftime('%Y-%m-%d')
            else:
                encoded_object = json.JSONEncoder.default(self, obj)
        except ValueError:
            encoded_object = '1900-01-01'
        return encoded_object


def json_encode(value):
    return json.dumps(value, cls=JSONExtensionEncoder).replace("</", "<\\/")


def json_decode(value):
    """Returns Python objects for the given JSON string."""
    return json.loads(to_basestring(value))

