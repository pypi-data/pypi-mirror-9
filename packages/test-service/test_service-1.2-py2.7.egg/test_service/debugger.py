# !/usr/bin/env python
# -*- coding: utf-8 -*-

u"""接口测试, 控制台只输出状态码和SQL语句, 不输出错误行.

    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', )
"""
__author__ = 'kylinfish@126.com'
__date__ = '2014/09/20'

import sys
import time
import traceback
from functools import wraps

import six

from .conf import post_data_print, post_data_saved, exec_time_print, save_rows_queue, service_debug, time_report
from .curl_builder import DataStore, cur_instance


time_instance = DataStore(report_file=time_report, maxsize=save_rows_queue)


class Timer(object):
    u"""Computer program exec time."""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        self.end = time.time()
        self.secs = self.end - self.start
        self.seconds = self.secs * 1000
        if self.verbose:
            six.print_('elapsed time: %f ms' % self.seconds)


def kylin_debug_request(func=None):
    u"""测试request函数, 打印出异常信息.

        :param func: view 函数
        不改变django settings LOGGING 配置, 既有代码不增加 try except.
    """

    if service_debug:
        @wraps(func)
        def returned_wrapper(request, *args, **kwargs):
            try:
                # 查看并控制台核实传入数据
                print_request_post(request)

                # 计算后端程序执行时间
                if exec_time_print:
                    with Timer() as t:
                        response = func(request, *args, **kwargs)

                    now_time = time.time()
                    six.print_("%s => %s ms" % (func.__name__, t.seconds))
                    line = "%-25s at %.2f %s => %s ms\n" % (func.__name__, now_time, 8 * ' ', t.seconds)
                    time_instance.save_line_data(line)
                else:
                    response = func(request, *args, **kwargs)

                return response

            except Exception as e:
                # 异常时保存下数据
                time_instance.save_file_data()
                cur_instance.save_file_data()

                six.print_(e)
                traceback.print_exc(file=sys.stdout)

        return returned_wrapper
    else:
        pass


def print_request_post(request):
    u"""输出并记录 request post(dict) 传入值, 此处也是为了捕获和验证参数, 捕获供 curl 再使用, 验证从 curl 传来值.
    """

    str_post = ''
    protocol = 'http://' if not request.is_secure() else 'https://'
    request_url = '%s%s%s\n' % (protocol, request.get_host(), request.get_full_path())

    if post_data_print:
        # 输出传入值开始
        six.print_('URL: %s' % request_url)

        if len(request.POST) > 0:
            six.print_('The following POST data: ')

            for (key, value) in request.POST.items():
                str_post = '&'.join((str_post, '%s=%s' % (key, value)))

                six.print_("    request.POST['%s'] = %s" % (key, value))

            str_post = str_post.strip('&')
            six.print_('\nPOST_DATA_STRING: %s' % str_post)

    if post_data_saved and str_post:
        # 记录传入值
        line = cur_instance.hold_data_require(request, request_url=request_url, data=str_post)
        cur_instance.save_line_data(line)
