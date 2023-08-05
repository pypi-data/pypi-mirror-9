# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'kylinfish@126.com'
__date__ = '2014/10/17'

u"""可以序列化 datetime, QuerySet 等多类型数据, 原来的查询集不用再 list() 处理了.

    python 2.6 以上自带的 json 处理库, Simplejson 是另一个Python JSON 编码和解码器,
    支持 Python 2.5+ 和 Python 3.3+, 为了加速处理速度，它包括一个可选的C扩展.

    datetime 依赖于django框架的库方法 DateTimeAwareJSONEncoder
"""

from types import ListType, DictType
from json import dumps
from decimal import Decimal

from django.db.models.query import QuerySet
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.contrib.gis import geos


def json_data_encode(json_data):
    u"""可以序列化 datetime, QuerySet 等多类型数据.

        :param json_data
    """

    def _any(data):

        if isinstance(data, ListType):
            return_data = _list(data)
        elif isinstance(data, DictType):
            return_data = _dict(data)
        elif isinstance(data, Decimal):
            return_data = str(data)
        elif isinstance(data, QuerySet):
            return_data = _list(data)
        elif isinstance(data, geos.Point):
            return_data = None
        else:
            return_data = data

        return return_data

    def _list(data):

        list_data = []
        for v in data:
            list_data.append(_any(v))
        return list_data

    def _dict(data):

        dict_data = {}
        for k, v in data.items():
            dict_data[k] = _any(v)
        return dict_data

    ret = _any(json_data)

    return dumps(ret, cls=DateTimeAwareJSONEncoder, ensure_ascii=False, indent=4)
