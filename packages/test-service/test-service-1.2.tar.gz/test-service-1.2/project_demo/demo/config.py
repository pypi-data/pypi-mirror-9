# !/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from .convert import MESSAGE_CODE_TEXT
except ImportError:
    MESSAGE_CODE_TEXT = None


def get_message_code(code):
    u"""由消息码获消息文本
    """

    if MESSAGE_CODE_TEXT:

        # 取消重复元素
        # new_tuple = tuple(set(MESSAGE_CODE_TEXT))

        text = ''
        for code_text in MESSAGE_CODE_TEXT:
            if code_text[0] == code:
                text = code_text[1]
                break
        return text
    else:
        return code


if __name__ == '__main__':
    u"""测试
    """

    # print get_message_code(3004)

    pass
