# !/usr/bin/env python
# -*- coding: utf-8 -*-

from json import dumps
# from simplejson import dumps
from django.conf import settings
from django.http import HttpResponse
from test_service.json_encoder import json_data_encode

from .config import get_message_code


def code_shift_text(dict_data):
    u"""转换消息数码到消息文本

    settings.py Add the following items:

        # 接口是否输出友好文本
        # False: 不显示; True: 显示
        IS_SHOW_MESSAGE_TEXT = True
    """

    is_show_message_text = getattr(settings, "IS_SHOW_MESSAGE_TEXT", False)

    if is_show_message_text:
        if 'error' in dict_data:
            dict_data['error_text'] = get_message_code(dict_data.get('error'))

    return dict_data


def duct_json(dict_data):
    u"""封装json返回数据
    """

    return HttpResponse(dumps(code_shift_text(dict_data), ensure_ascii=False))


def duct_json_data(dict_data):
    u"""封装json返回数据
    """

    return HttpResponse(json_data_encode(code_shift_text(dict_data)))