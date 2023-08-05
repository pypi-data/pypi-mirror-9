# -*- encoding: utf-8 -*-

import datetime
import time


def h2u(value, view='%Y-%m-%d %H:%M:%S', unix_int=True):
    """
    Convert str in format (view) to unix time
    :param value: string of date
    :param view: format string
    :param unix_int: return unix time as int value
    :return: unix time (int value)
    """
    try:
        result = time.mktime(datetime.datetime.strptime(value, view)
                             .timetuple())
        result = int(result) if unix_int else result
    except ValueError as e:
        raise ValueError("Exception from dateconv: %s" % str(e))
    else:
        return result


def d2u(value, unix_int=True):
    """
    Convert datetime object  to unix time
    :param value: datetime.datetime object
    :param unix_int: return unix time as int value
    :return: unix time (int value)
    """
    try:
        result = time.mktime(value.timetuple())
        result = int(result) if unix_int else result
    except ValueError as e:
        raise ValueError("Exception from dateconv: %s" % str(e))
    else:
        return result


def u2d(value, unix_int=True):
    """
    Convert unix time to datetime
    :param value: datetime object
    :param unix_int: before converting to datetime, convert unix time to int
    :return:
    """
    try:
        value = int(value) if unix_int else value
        result = datetime.datetime.fromtimestamp(value)
    except ValueError as e:
        raise ValueError("Exception from dateconv: %s" % str(e))
    else:
        return result


def h2d(value, view='%Y-%m-%d %H:%M:%S', unix_int=True):
    """
    Convert str in format %view% to datetime
    :param value: datetime object
    :param view: format string
    :param unix_int: before converting to datetime, convert unix time to int
    :return:
    """
    try:
        result = u2d(h2u(value, view, unix_int))
    except ValueError as e:
        raise ValueError("Exception from dateconv: %s" % str(e))
    else:
        return result


def d2h(value, view='%Y-%m-%d %H:%M:%S'):
    """
    Convert datetime object to str in format
    :param value: datetime.datetime object
    :return: unix time (int value)
    """
    try:
        result = value.strftime(view)
    except ValueError as e:
        raise ValueError("Exception from dateconv: %s" % str(e))
    else:
        return result


def u2h(value, view='%Y-%m-%d %H:%M:%S', unix_int=True):
    """
    Convert unix time to datetime object
    :param value: unix_time (int value)
    :param view: format to string
    :param unix_int: before converting to datetime, convert unix time to int
    :return:
    """
    try:
        value = int(value) if unix_int else value
        result = d2h(datetime.datetime.fromtimestamp(value), view)
    except ValueError as e:
        raise ValueError("Exception from dateconv: %s" % str(e))
    else:
        return result
