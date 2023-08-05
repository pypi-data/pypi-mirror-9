#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""对拦截curl记录保存文件, 做处理去掉重复行.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/14'

from django.core.management.base import NoArgsCommand
from test_service.curl_builder import sole_file_data, cur_instance


class Command(NoArgsCommand):
    help = u"对拦截curl记录保存文件, 做处理去掉重复行."

    def handle_noargs(self, **options):
        sole_file_data(cur_instance, '_curl.md', '_sole.md')
