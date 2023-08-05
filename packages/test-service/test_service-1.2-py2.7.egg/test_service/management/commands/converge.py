#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""从源码文件中生成 消息码/消息文本配置信息.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/14'

from django.core.management.base import NoArgsCommand

from test_service.conf import converge_list
from test_service.converge import ConvergeSRC


class Command(NoArgsCommand):
    help = "从源码文件中生成 消息码/消息文本配置信息."

    def handle_noargs(self, **options):
        ConvergeSRC(converge_list).exec_script_line()
