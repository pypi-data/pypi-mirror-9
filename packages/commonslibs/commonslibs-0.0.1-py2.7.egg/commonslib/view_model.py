#!/usr/bin/env python
# -*- coding: utf-8 -*-
from decorated.base.dict import DefaultDict

__author__ = 'freeway'


class ViewModel(DefaultDict):

    def __init__(self, default='', **kw):
        super(ViewModel, self).__init__(default, **kw)

    @staticmethod
    def to_views(biz_models):
        if biz_models is None or len(biz_models) == 0:
            return []
        else:
            return [ViewModel(**biz_model.attributes) for biz_model in biz_models]

    @staticmethod
    def to_view(biz_model):
        return ViewModel(**biz_model.attributes)