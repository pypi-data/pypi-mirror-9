# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

u"""从源码文件中生成 消息码/消息文本配置信息.

    匹配格式如下:
        return duct_json({'error': 0000})  # 消息文本
        return duct_json_data({'error': 0000})  # 消息文本

        return 0000  # 消息文本

    读取指定的文件, 查找匹配的信息并保存到配置文件.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2014/10/27'

import os
import sys
import six
import os.path
from datetime import datetime
from conf import converge_conf
# from conf_no_settings import converge_conf

reload(sys)
# noinspection PyUnresolvedReferences
sys.setdefaultencoding('utf-8')


class ConvergeSRC(object):
    def __init__(self, script_files):
        """
            :param script_files: 源文件全路径, 支持单文件多文件模式.
        """

        self.script_files = script_files
        self.result_log_name = None  # 查找结果保存文件名

    def exec_script_line(self):
        u"""运行指定行范围脚本.
        """

        lines = []
        if isinstance(self.script_files, list):
            for script_file in self.script_files:
                file_lines = self.read_script_line(script_file)
                if file_lines:
                    lines.extend(file_lines)
        else:
            lines = self.read_script_line(self.script_files)

        if lines:
            self.result_log_name = self.__path_result_file()
            # 输出头部信息
            self.__write_head_line()
            # 消息码记录
            message_code_dict = {}

            def write_dict_data(code, text):
                u"""去重, 数据暂写入字典.

                    :param code: 数字码
                    :param text: 文本
                """

                # 系统消息码使用场合太多, 行后注释不是一定存在的处理(or).
                if code not in message_code_dict.keys() or not message_code_dict[code]:
                    message_code_dict[code] = text

            for line in lines:
                msg_code, msg_text = self.match_line_find(line)
                # msg_code, msg_text = match_line_split(line)

                if msg_code is not None:
                    if converge_conf['is_distinct_sort']:
                        write_dict_data(msg_code, msg_text)
                    else:
                        os.system(converge_conf['data_format_string'] % (msg_code, msg_text, self.result_log_name))

            if converge_conf['is_distinct_sort']:
                # code_text = sorted(message_code_dict.items(), key=lambda d: d[1])  # 按照value排序
                code_text = sorted(message_code_dict.items(), key=lambda d: d[0])  # 按照key排序

                for (key, value) in code_text:
                    os.system(converge_conf['data_format_string'] % (key, value, self.result_log_name))

                message_code_dict.clear()

            # 输出尾部信息
            self.__write_tail_line()

    def __path_result_file(self):
        u"""生成配置数据的存放目录.
        """

        if isinstance(self.script_files, list):
            # 多文件模式, 以第一文件为数据保存路径
            script_file = self.script_files[0]
        else:
            script_file = self.script_files

        # 设置最后目录
        result_file_path = os.path.dirname(script_file)

        # 创建目录
        if not os.path.exists(result_file_path):
            os.makedirs(result_file_path)

        # 最后文件
        log_file_name = os.path.join(result_file_path, converge_conf['output_file_name'])

        # 如文件存在删除
        if os.path.exists(log_file_name):
            os.remove(log_file_name)

        return log_file_name

    @staticmethod
    def read_script_line(read_file):
        u"""读取测试脚本文件内容.

            :param read_file: 文件
        """

        if os.path.exists(read_file):
            if os.path.ismount(read_file) or os.path.isdir(read_file):
                six.print_(u'亲, 指定的存储路径错误！')
                return

            script_log_file = open(read_file, 'rb')
            lines = script_log_file.readlines()

            if lines:
                return lines
            else:
                six.print_(u'测试脚本, 指定的文件内容为空.')
        else:
            six.print_(u'测试脚本, 指定的文件不存在.')

        return None

    def __write_head_line(self):
        u"""输出头部信息.

        """

        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        comments = r"# !/usr/bin/env python\n# -*- coding: utf-8 -*-\n\nu\"\"\"" \
                   + r"消息数字码/消息友好文本 配置数据文件. 该文件由工具 %s 生成, 生成时间 %s.\n" % (os.path.basename(__file__), now_time) \
                   + r"\"\"\"\n\n"

        os.system("""echo "%s" >> %s""" % (comments, self.result_log_name))
        os.system("""echo "MESSAGE_CODE_TEXT = (" >> %s""" % self.result_log_name)

    def __write_tail_line(self):
        u"""输出尾部信息.
        """

        os.system("""echo ")" >> %s""" % self.result_log_name)

    @classmethod
    def match_line_find(cls, line):
        u"""处理某些过滤表达式, 以find形式定位查找点.

            :param line: 行内容
        """

        msg_code, msg_text = None, None
        line = line.strip().replace("\n", "")

        sign_code = "'error':"  # 标识
        sign_text = "#"  # 标识

        if line.startswith("return duct_json"):

            # 消息码查找
            if line.find(sign_code) > 0:
                code_head = line.index(sign_code) + len(sign_code)  # 索引起点

                sharp_index = line.find(sign_text)
                if sharp_index > 0:
                    point_index = line[code_head:sharp_index].find(',')  # 索引终点
                else:
                    point_index = line[code_head:].find(',')  # 索引终点

                if point_index > 0:
                    code_tail = code_head + point_index
                else:
                    code_tail = code_head + line[code_head:].index('}')

                msg_code = line[code_head:code_tail].strip()
                try:
                    msg_code = int(msg_code)
                except (TypeError, ValueError):
                    msg_code = None

            # 消息文本查找
            if msg_code is not None:
                try:
                    text_head = line.rindex(sign_text)
                except ValueError:
                    text_head = None

                if text_head:
                    # 清除首尾多余的空白, 单引号, 以及首字符编码符号
                    msg_text = line[text_head + 1:].strip().strip('\'').lstrip('u\'')
                else:
                    msg_text = ''

        elif line.startswith("return ") and line.count('#') > 0:
            msg_code, msg_text = cls.match_line_digit(line)

        return cls.code_system_text(msg_code, msg_text)

    @classmethod
    def match_line_split(cls, line):
        u"""处理某些过滤表达式, 以split形式定位查找点.

            :param line: 行内容
        """

        msg_code, msg_text = None, None
        line = line.strip().replace("\n", "")

        sign_code = "'error':"  # 标识
        sign_text = "#"  # 标识

        if line.startswith("return duct_json"):

            # 查找 msg_code:
            if line.find(sign_code) > 0:
                line_tail = line.split(sign_code)[-1].split(sign_text)[0].strip()

                try:
                    code_tail = line_tail.index(',')  # 索引终点
                except ValueError:
                    code_tail = line_tail.index('}')

                msg_code = line_tail[:code_tail]

                try:
                    msg_code = int(msg_code)
                except (TypeError, ValueError):
                    msg_code = None

            # 查找 msg_text:
            if msg_code:
                if line.find(sign_text) > 0:
                    msg_text = line.split(sign_text)[-1].strip().strip('\'').lstrip('u\'')
                else:
                    msg_text = ''

        elif line.startswith("return ") and line.count('#') > 0:
            msg_code, msg_text = cls.match_line_digit(line)

        return cls.code_system_text(msg_code, msg_text)

    @staticmethod
    def match_line_digit(line):
        u"""处理某些过滤表达式.

            :param line: 行内容

            匹配格式如下:
                return 0000  # 消息文本
        """

        if line.startswith("return ") and line.count('#') > 0:
            msg_code = line.split()[1].strip()

            try:
                msg_code = int(msg_code)
            except (TypeError, ValueError):
                msg_code = None

            msg_text = line.split('#')[-1].strip().strip('\'').lstrip('u\'')
            return msg_code, msg_text

    @staticmethod
    def code_system_text(code, text):
        u"""系统消息码使用场合太多, 行后注释未必存在的处理.

            :param code: 数字码
            :param text: 文本

            注意：字符窜类型前缀'r'不能改变为'u'.
        """

        if code == 0:
            text = 'ok'
        elif code == 8888:
            text = r'请求参数错误'
        elif code == 9999:
            text = r'系统错误信息'

        return code, text


def runner_console():
    u"""命令行传值执行.
    """

    arg_file_path = None
    arg_len = len(sys.argv)

    if arg_len > 1:
        arg_file_path = sys.argv[1:]

    ConvergeSRC(arg_file_path).exec_script_line()


if __name__ == '__main__':
    u"""单元测试.
    """

    six.print_(u'Beginning...')

    runner_console()

    # pass
