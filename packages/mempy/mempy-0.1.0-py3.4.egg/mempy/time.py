# *-* coding: UTF8 -*-
#==============================================================================
"""
[time.py] - Mempire Time module

이 모듈은 시간/날짜계산 기능을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__ver__ = '150114'
__since__ = '2006-10-01'
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


import datetime


class TimeTypeError(Exception):pass


def get_days_from_timedelta(fromtime, totime):
    """get_days_from_timedelta(fromtime,totime) -> integer
    Returns days between fromtime and totime.
    - 'fromtime, 'totime' is a tuple like (2007, 5, 29, 20, 16).
    - Returned integer can be minus if totime precides fromtime.
    """

    try:
        ftime = datetime.datetime(fromtime[0],fromtime[1],fromtime[2],fromtime[3],fromtime[4])
        ttime = datetime.datetime(totime[0],totime[1],totime[2],totime[3],totime[4])
    except:
        raise TimeTypeError
        return

    timegap = ttime - ftime
    return timegap.days


def get_mins_from_timedelta(fromtime, totime):
    """get_mins_from_timedelta(fromtime,totime) -> integer or long
    Returns minutes between fromtime and totime.
    - 'fromtime' & 'totime' is a tuple like (2007, 5, 29, 20, 16).
    - if totime precedes fromtime, minus value will be returned.
    """

    try:
        ftime = datetime.datetime(fromtime[0],fromtime[1],fromtime[2],fromtime[3],fromtime[4])
        ttime = datetime.datetime(totime[0],totime[1],totime[2],totime[3],totime[4])
    except:
        raise TimeTypeError
        return

    timegap = ttime - ftime
    daynum = timegap.days

    return daynum * 1440 + timegap.seconds//60


def get_date_after_mins(minute, fromtime):
    """get_date_after_mins(minute, fromtime) -> tuple
    Returns date after timedelta.
    - 'minute' is integer or long value(it can be minus).
    - 'fromtime' & Returned value is a tuple like (2007, 5, 29, 20, 16).
    """

    #Verify Input
    #if minute < 0:
    #    raise TimeTypeError
    #    return
    try:
        ftime = datetime.datetime(fromtime[0],fromtime[1],fromtime[2],fromtime[3],fromtime[4])
    except:
        raise TimeTypeError
        return

    days = minute // 1440
    seconds = (minute - days*1440)*60
    tdelta = datetime.timedelta(days,seconds)
    ttime = ftime + tdelta

    return ttime.year, ttime.month, ttime.day,\
            ttime.hour, ttime.minute


def isEarlier(atime, btime):
    """isEarlier(atime, btime) -> boolean
    Returns True if atime is earlier than btime.
    - 'atime' & 'btime' is a tuple like (2007, 5, 29, 20, 16).
    """

    try:
        ftime = datetime.datetime(atime[0],atime[1],atime[2],atime[3],atime[4])
        ttime = datetime.datetime(btime[0],btime[1],btime[2],btime[3],btime[4])
    except:
        raise TimeTypeError
        return

    timegap = ttime - ftime
    if timegap.days > 0:
        return True
    else:
        if timegap.days == 0 and timegap.seconds > 0:
            return True
        else:
            return False

