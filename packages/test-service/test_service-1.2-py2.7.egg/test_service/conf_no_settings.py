# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/14'

import os
from os.path import join, dirname

project_path = os.path.dirname(os.path.abspath(__file__))
service_debug = True

post_data_print = True  # 是否输入POST数据
post_data_saved = True  # 是否保存请求痕迹
exec_time_print = True  # 是否输出执行时间
save_rows_queue = 5  # 是否输出执行时间

LOGIN_API = ('/user/login/', '/user/join/',)
LOGOUT_API = ('/user/logout/',)

# service API 执行时间保存文件
# noinspection PyUnresolvedReferences
time_report = join(dirname(project_path), 'report', r'report_time.md')

# 拦截生成curl保存文件
# noinspection PyUnresolvedReferences
curl_report = join(dirname(project_path), 'report', r'report_curl.md')

converge_conf = {
    # 查找结果保存文件名
    'output_file_name': "convert.py",

    # 是否取消重复行并排序
    'is_distinct_sort': True,

    # 数据保存到文件字符串格式
    'data_format_string': r"""echo "    (%s, u'%s'), " >> %s""",
}


# 要查找源文件路径
converge_file = ['views.py']
# noinspection PyUnresolvedReferences
converge_list = [os.path.join(os.path.join(project_path, 'demo'), uni_file) for uni_file in converge_file]
