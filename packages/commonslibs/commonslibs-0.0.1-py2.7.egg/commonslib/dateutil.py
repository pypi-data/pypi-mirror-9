#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime


def offset_time(date_time):
    """获取偏移时间.

    :param date_time: string，传入的的参数为时间字符串如：2011-04-25 22:08:21
    :return: 返回string， 刚刚、5秒前、10分钟前等偏移时间
    """

    dis = time.mktime(datetime.datetime.now().timetuple())-time.mktime(date_time.timetuple())
    onesecond = 1
    oneminute = onesecond*60
    onehour = oneminute*60
    oneday = onehour*24
    oneweek = oneday*7
    onemonth = oneday*30
    if dis < 2:
        distance = u"刚刚"
    elif dis/oneminute < 1:
        distance = str(int(dis/onesecond))+u"秒前"
    elif dis/onehour < 1:
        distance = str(int(dis/oneminute))+u"分钟前"
    elif dis/oneday < 1:
        distance = str(int(dis/onehour))+u"小时前"
    elif dis/oneweek < 1:
        distance = str(int(dis/oneday))+u"天前"
    elif dis/onemonth < 1:
        distance = str(int(dis/oneweek))+u"周前"
    elif dis/onemonth < 12:
        distance = str(int(dis/onemonth))+u"个月前"
    else:
        distance = time.strftime(u"Y年m月d日", date_time)
    return distance


def timestamp(date_time=None):
    if date_time is None:
        date_time = datetime.datetime.now()
    """返回13位的时间戳，精确到毫秒
    :return: 13位的时间戳
    """
    return long(time.mktime(date_time.timetuple()))*1000+date_time.microsecond/1000


def datetime_to_string(date_time, format_str='%Y-%m-%d'):
    """将datetime数据类型转换成字符类型

    :param date_time: datetime类型的数据结构
    :param format_str: 字符串的时间显示样式
    :return: 时间样式的字符串
    """
    if date_time is None:
        return ''
    else:
        return date_time.strftime(format_str)


def string_to_date(date_str, format_str='%Y-%m-%d'):
    """将字符串转换成date

    :param date_str: 日期字符串
    :param format_str:日期字符串对应的格式
    :return: date数据类型
    """
    if isinstance(date_str, datetime.date):
        return date_str
    if date_str is None or len(date_str.strip()) == 0:
        return None
    return datetime.datetime.strptime(date_str, format_str).date()


def string_to_datetime(datetime_str, format_str='%Y-%m-%d'):
    """将字符串转换成datetime

    :param datetime_str: 日期时间字符串
    :param format_str: 日期时间字符串对应的格式
    :return: datetime数据类型
    """
    if isinstance(datetime_str, datetime.datetime):
        return datetime_str
    if datetime_str is None or len(datetime_str.strip()) == 0:
        return None
    return datetime.datetime.strptime(datetime_str, format_str)


def string_to_timestamp(date_str, format_str='%Y-%m-%d'):
    """字符串转换成timestamp

    :param date_str: 日期时间字符串
    :param format_str: 日期时间字符串对应的格式
    :return: 13位的时间戳
    """
    return timestamp(string_to_datetime(date_str, format_str))


def timestamp_to_datetime(time_stamp):
    """时间戳转换成datetime类型

    :param time_stamp: 时间戳
    :return: datetime数据类型
    """
    if time_stamp > 10000000000:
        return datetime.datetime.fromtimestamp(time_stamp/1000)
    else:
        return datetime.datetime.fromtimestamp(time_stamp)


def timestamp_to_string(time_stamp, format_str='%Y-%m-%d'):
    """时间戳转换成字符串

    :param time_stamp: 13位时间戳
    :param format_str: 转换的日期时间字符串格式
    :return: 日期时间字符串
    """
    return datetime_to_string(timestamp_to_datetime(time_stamp), format_str)

def today_timestamp():
    """
    返回今天的时间戳
    :return:
    """
    return string_to_timestamp(str(datetime.date.today()))

if __name__ == "__main__":
    print datetime_to_string(datetime.datetime.now())
    print datetime_to_string(None)
    print timestamp_to_string(1316534399, '%Y-%m-%d %H:%M:%S')
    print timestamp()
    time.sleep(2)
    print timestamp()
    print time.time()
    print time.mktime(time.localtime())
    time_time = time.localtime(1316534399)
    print datetime.datetime.fromtimestamp(1316534399)
    print timestamp_to_datetime(1316534399000).__class__
    print timestamp_to_datetime(1316534399000)

    print string_to_date('2014-12-11').__class__
    print string_to_datetime('2014-12-11')
    #print datetime_to_string(timestamp_to_datetime(1316534399000))
    print time.strftime('%Y-%m-%d %H:%M:%S', time_time)
    print timestamp_to_string(1316534399, '%Y-%m-%d %H:%M:%S')

    print string_to_timestamp('2014-12-11', '%Y-%m-%d')
    print timestamp_to_string(string_to_timestamp('2014-12-12', '%Y-%m-%d') + 24*60*60*1000, '%Y-%m-%d %H:%M:%S')
