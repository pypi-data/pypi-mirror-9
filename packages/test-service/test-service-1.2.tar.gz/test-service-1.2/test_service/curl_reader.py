# !/usr/bin/env python
# -*- coding: utf-8 -*-

u"""读取存放测试脚本的文件, 以命令行的形式执行指定的行脚本, 指定范围的行脚本.

    利用 linux curl 构建测试脚本, 减少服务端开发过程中, 在测试上对客户端的依赖.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2014/10/27'

import os
import os.path
from .conf import curl_report, project_path

import six

if six.PY3:
    range_ = range
else:
    range_ = xrange


class ScriptExecute(object):
    u"""读取测试脚本, 执行行脚本, 指定范围的行脚本
    """

    def __init__(self, script_file, report_bool=True, lazy_bone=None):
        """
            :param script_file:
            :param report_bool:
            :param lazy_bone:
        """

        super(ScriptExecute, self).__init__()
        self.script_file = script_file
        self.report_bool = report_bool  # 是否生成报告文件
        self.lazy_bone = lazy_bone
        self.log_file_name = None
        self.script_lines = None

    def __path_result_file(self):
        u"""生成日志的目录及文件形式.
        """

        # noinspection PyUnresolvedReferences
        result_file_logs = os.path.join(os.path.dirname(project_path), r'log')  # 默认报告目录

        if not os.path.exists(result_file_logs):
            os.makedirs(result_file_logs)

        if not self.log_file_name:
            # noinspection PyUnresolvedReferences
            log_file_name = os.path.join(result_file_logs, u'curl_%s.htm')

            self.log_file_name = log_file_name

        return self.log_file_name

    def __read_script_file(self):
        u"""读取测试脚本文件内容.
        """

        if not self.script_lines and os.path.exists(self.script_file):

            if os.path.ismount(self.script_file) or os.path.isdir(self.script_file):
                six.print_(u'亲, 指定的存储路径错误！')
                return

            script_log_file = open(self.script_file, 'rb')
            lines = script_log_file.readlines()

            if lines:
                self.script_lines = lines
            else:
                six.print_(u'测试脚本, 指定的文件内容为空.')
        else:
            six.print_(u'测试脚本, 指定的文件不存在.')

        return self.script_lines

    def __loop_line(self, num, lines):
        u"""运行行列表里指定的行.

            :param num: 行号
            :param lines: 行列表
        """

        log_name = self.__path_result_file() % num
        if num > 0:
            num -= 1  # 文档行标, 实例索引起点不一

        line = lines[num].strip().replace("\n", "")

        # six.print_(line)
        # six.print_(line.startswith('curl')
        if line.startswith('curl'):
            if self.lazy_bone:
                line = self.lazy_bone.process_regular(line)
            six.print_(90 * '=')
            six.print_(line.split()[-1])

            if self.report_bool:
                os.system('%s > %s' % (line, log_name))
            else:
                os.system('%s' % line)

    def run_script_line(self, num=-1):
        u"""运行指定行脚本.

            :param num: 行号, 默认最后行
        """

        lines = self.__read_script_file()
        if lines:
            self.__loop_line(num, lines)

    def run_script_lines(self, start=0, count=0):
        u"""运行指定行范围脚本.

            :param start: 起始行号 整数
            :param count: 后面行数 正整数
        """

        lines = self.__read_script_file()
        if lines:
            if len(lines) >= abs(start):
                if count == 0:
                    self.__loop_line(start, lines)
                else:
                    for i in range_(start, start + count):
                        if i == len(lines):
                            break

                        self.__loop_line(i, lines)


class LazyBone(object):
    u"""处理某些正则表达式, 懒人而已.
    """

    def __init__(self, regulars, exam_ids):
        """
            :param regulars: 要替换的表达式
            :param exam_ids: 被替换为的值
        """

        # [r'(?P<user_id>\d+)', r'(?P<tip_id>\d+)', r'(?P<place_id>\d+)']  # 三者不会同时存在
        # ['624', '26774', '1294']  # 待用于测试的实例依次ID

        self.regulars = regulars
        self.exam_ids = exam_ids

    def process_regular(self, line):
        u"""处理某些正则表达式.

            :param line: 行内容
        """

        for i in range_(len(self.regulars)):
            if line.find(self.regulars[i]) < 0:
                continue

            line = line.replace(self.regulars[i], self.exam_ids[i])
            break

        return line


curl_script = ScriptExecute(curl_report)
