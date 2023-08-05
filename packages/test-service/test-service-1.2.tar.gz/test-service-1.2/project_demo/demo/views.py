# !/usr/bin/env python
# -*- coding: utf-8 -*-

from .common import duct_json, duct_json_data
from test_service.debugger import kylin_debug_request


@kylin_debug_request
def test(request):
    u"""
    """

    error = 9999
    if request.method != 'POST':
        return duct_json({'error': error})


@kylin_debug_request
def demo(request):
    u"""
    """

    result_data = []

    for (key, value) in request.POST.items():
        result_data.append(value)

    return duct_json_data({'error': 0, 'data': result_data})  # ok, success.
