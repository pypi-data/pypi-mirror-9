# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

u"""拦截request, 构建curl脚本, 并存储类.
    没使用middleware的形式, 拦截所需service, 使定义更灵活.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2014/11/08'

import os
from datetime import datetime

import six

from .conf import curl_report, login_api, logout_api, save_rows_queue


if six.PY3:
    from queue import Queue
else:
    from Queue import Queue


class DataStore(object):
    u"""数据行存储类.
    """

    def __init__(self, report_file, maxsize=5):
        super(DataStore, self).__init__()
        self._report_file = report_file
        self._lines_store = Queue(maxsize=maxsize)

        # 创建存放的路径
        dir_path = os.path.dirname(self._report_file)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def get_report_file(self):
        return self._report_file

    def open_file_data(self):
        u"""读取报告文件
        """

        if os.path.exists(self._report_file):
            read_file = open(self._report_file, 'rb')
            return read_file.readlines()

        return None

    def save_line_data(self, line):
        u"""保存行数据.

            :param line
        """

        # 存储到队列
        if not self._lines_store.full():
            self._lines_store.put(line)

        # 从队列中保存
        if self._lines_store.full():
            self.save_file_data()

    def save_file_data(self):
        u"""存储数据到文件.
        """

        with open(self._report_file, 'ab') as f:
            if not self._lines_store.empty():
                log_time = '#### %s\n' % str(datetime.now())
                f.write(log_time)

            while not self._lines_store.empty():
                one = self._lines_store.get()
                f.write('\t%s' % one)


class RequireStore(DataStore):
    u"""拦截request, 构建curl脚本, 并存储类.
    """

    _LOGIN_API = login_api
    _LOGOUT_API = logout_api

    def __init__(self, report_file, maxsize=0, cookie=None):
        super(RequireStore, self).__init__(report_file, maxsize)
        self.cookie = cookie

    def hold_data_require(self, request, request_url=None, data=None):
        """构建脚本, 生成curl 命令行.

            :param request
            :param request_url
            :param data

            仅支持:
            method: GET/POST 其它如有需要待扩展
            protocol: http/https 其它不考虑
        """

        line = 'curl '
        # 会话 cookies
        if self.cookie:
            # Fixed: -D and -b together error.
            if request.get_full_path() in self._LOGIN_API + self._LOGOUT_API:
                line = ''.join((line, '-D %s ' % self.cookie))
            else:
                line = ''.join((line, '-b %s ' % self.cookie))

        # 构建方法和数据
        if request.method == 'POST' and data:
            line = ''.join((line, '-d \"%s\" ' % data))
        elif request.method == 'GET' and data:
            line = ''.join((line, '-G \"%s\" ' % data))
        else:
            pass

        # 构建请求地址
        if not request_url:
            protocol = 'http://' if not request.is_secure() else 'https://'
            request_url = '%s%s%s' % (protocol, request.get_host(), request.get_full_path())

        line = ''.join((line, request_url))
        return line


def sole_file_data(instance, orig_sign, sole_sign):
    u"""对拦截curl记录保存文件, 做处理去掉重复行.

        :param instance: DataStore实例
        :param orig_sign: 老文件标识
        :param sole_sign: 新文件标识
    """

    lines = instance.open_file_data()
    if lines:
        sole_file = instance.get_report_file().replace(orig_sign, sole_sign)  # 去重后的记录文件
        if os.path.exists(sole_file):
            os.remove(sole_file)  # 删除之前生成文件

        six.print_('Original: %s' % len(lines))
        sole_data = set(lines)
        num_date = 0

        with open(sole_file, 'ab') as rf:
            for _line_ in sole_data:
                if _line_.startswith('####'):  # 取消原来日期分组
                    num_date += 1
                    continue
                rf.write(_line_)

        six.print_('Nowadays: %s' % (len(sole_data) - num_date))
        six.print_('All is Ok')
    else:
        six.print_('Data is None')


cur_instance = RequireStore(report_file=curl_report, maxsize=save_rows_queue, cookie='./log/cookie.txt')
