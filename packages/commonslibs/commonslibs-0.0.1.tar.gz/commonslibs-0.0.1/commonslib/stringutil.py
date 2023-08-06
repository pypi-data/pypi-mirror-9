#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2011-6-15
字符串帮助类
@author: huwei
"""
import string
import random
import hashlib
import uuid

def random_string(length=8):
    """生成随机字符串.

    :param length:随机字符串长度，默认为8
    :return: 返回随机字符串
    """
    return ''.join(random.sample(string.ascii_letters+string.digits, length))


def random_number(length=6):
    """生成随机数字.

    :param length:随机字符串长度，默认为8
    :return: 返回随机字符串
    """
    return ''.join(random.sample(string.digits, length))


def convert_to_utf8(s):
    """非UTF8字符串.

    :param s: 转换成UTF8字符串.
    :return: UTF8字符串.
    """
    return s.encode('utf8')


def addslashes(s):
    d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\"}
    return ''.join(d.get(c, c) for c in s)


def md5(s):
    return hashlib.md5(s).hexdigest()


def uuid4():
    """生成uuid4的字符串
    :return:
    """
    return str(uuid.uuid4())


def get_first_char(src):
    
    first_char_ord = ord(src[0].upper())
    if (first_char_ord >= 65 and first_char_ord <= 91)or(first_char_ord >= 48 and first_char_ord <= 57):
        return src[0].upper()
    target = src.encode(u"GB18030")
    asc = ord(target[0])*256+ord(target[1])-65536
    if asc >= -20319 and asc <= -20284:
        return 'A'
    if asc >= -20283 and asc <= -19776:
        return 'B'
    if asc >= -19775 and asc <= -19219:
        return 'C'
    if asc >= -19218 and asc <= -18711:
        return 'D'
    if asc >= -18710 and asc <= -18527:
        return 'E'
    if asc >= -18526 and asc <= -18240:
        return 'F'
    if asc >= -18239 and asc <= -17923:
        return 'G'
    if asc >= -17922 and asc <= -17418:
        return 'H'
    if asc >= -17417 and asc <= -16475:
        return 'J'
    if asc >= -16474 and asc <= -16213:
        return 'K'
    if asc >= -16212 and asc <= -15641:
        return 'L'
    if asc >= -15640 and asc <= -15166:
        return 'M'
    if asc >= -15165 and asc <= -14923:
        return 'N'
    if asc >= -14922 and asc <= -14915:
        return 'O'
    if asc >= -14914 and asc <= -14631:
        return 'P'
    if asc >= -14630 and asc <= -14150:
        return 'Q'
    if asc >= -14149 and asc <= -14091:
        return 'R'
    if asc >= -14090 and asc <= -13119:
        return 'S'
    if asc >= -13118 and asc <= -12839:
        return 'T'
    if asc >= -12838 and asc <= -12557:
        return 'W'
    if asc >= -12556 and asc <= -11848:
        return 'X'
    if asc >= -11847 and asc <= -11056:
        return 'Y'
    if asc >= -11055 and asc <= -10247:
        return 'Z'
    if asc == -9767:
        return 'D'
    if asc == -9743 or asc == -6155:
        return 'H'
    if asc == -3372:
        return 'J'
    if asc == -6993 or asc == -6928 or asc == -2633 or asc == -7182:
        return 'L'
    if asc == -6745:
        return 'P'
    if asc == -7703:
        return 'Q'
    if asc == -7725:
        return 'S'
    if asc == -5128:
        return 'T'
    if asc == -8962 or asc==-9744:
        return 'Y'
    if asc == -6973:
        return 'Z'
    print asc
    return ''


if __name__ == "__main__":
    print get_first_char(u'珲春')
    print get_first_char(u'浏')
    print get_first_char(u'醴陵')
    print get_first_char(u'衢州')
    print get_first_char(u'泸州')
    print get_first_char(u'滕州')
    print get_first_char(u'兖州')
    print get_first_char(u'蛟河')
    print get_first_char(u'荥阳')
    print get_first_char(u'濮阳')
    print get_first_char(u'涿州')
    print get_first_char(u'亳州')
    print get_first_char(u'漯河')
    print get_first_char(u'儋州')
    print get_first_char(u'嵊州市')
    print get_first_char(u'万州')
    print len(u'c')
    print get_first_char(u'mark')
    print convert_to_utf8(u'中国')
    print random_string(8)
    
    print u'漯河,万州,'.split(',')
    print u'万州'.split(',')


