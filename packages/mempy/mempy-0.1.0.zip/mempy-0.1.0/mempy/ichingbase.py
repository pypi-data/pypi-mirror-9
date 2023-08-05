# *-* coding: UTF8 -*-
#==============================================================================
"""
[ichingbase.py] - Mempire Iching System Base module

이 모듈은 주역명리시스템(ex. 입춘/동지날짜와 계산)의 기본이 되는 
기능을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__ver__ = '150114'
__since__ = '2006-10-01'
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


import time
from mempy import time as mytime


class TimeTypeError(Exception):pass


GAPJA60 = {
'0':'aa','1':'bb','2':'cc','3':'dd','4':'ee','5':'ff','6':'gg','7':'hh','8':'ii','9':'jj',
'10':'ak','11':'bl','12':'ca','13':'db','14':'ec','15':'fd','16':'ge','17':'hf','18':'ig','19':'jh',
'20':'ai','21':'bj','22':'ck','23':'dl','24':'ea','25':'fb','26':'gc','27':'hd','28':'ie','29':'jf',
'30':'ag','31':'bh','32':'ci','33':'dj','34':'ek','35':'fl','36':'ga','37':'hb','38':'ic','39':'jd',
'40':'ae','41':'bf','42':'cg','43':'dh','44':'ei','45':'fj','46':'gk','47':'hl','48':'ia','49':'jb',
'50':'ac','51':'bd','52':'ce','53':'df','54':'eg','55':'fh','56':'gi','57':'hj','58':'ik','59':'jl'}

GAPJA60h = {
'0':'甲子','1':'乙丑','2':'丙寅','3':'丁卯','4':'戊辰','5':'己巳','6':'庚午','7':'辛未','8':'壬申','9':'癸酉',
'10':'甲戌','11':'乙亥','12':'丙子','13':'丁丑','14':'戊寅','15':'己卯','16':'庚辰','17':'辛巳','18':'壬午','19':'癸未',
'20':'甲申','21':'乙酉','22':'丙戌','23':'丁亥','24':'戊子','25':'己丑','26':'庚寅','27':'辛卯','28':'壬辰','29':'癸巳',
'30':'甲午','31':'乙未','32':'丙申','33':'丁酉','34':'戊戌','35':'己亥','36':'庚子','37':'辛丑','38':'壬人','39':'癸卯',
'40':'甲辰','41':'乙巳','42':'丙午','43':'丁未','44':'戊申','45':'己酉','46':'庚戌','47':'辛亥','48':'壬子','49':'癸丑',
'50':'甲寅','51':'乙卯','52':'丙辰','53':'丁巳','54':'戊午','55':'己未','56':'庚申','57':'辛酉','58':'壬戌','59':'癸亥'}

JEOLKI_GAP_FROM_IPCHUN = (0,21355,42843,64498,86335,108366,130578,152958,
                175471,198077,220728,243370,265955,288432,310767,332928,
                354903,376685,398290,419736,441060,462295,483493,504693)

# '~'는 천간, '_'는 지지, '@'은 구성, '#'은 팔문, '$'은 팔신, '?'는 공망
SYMBOL2UNICODE_TABLE ={
"~a":"甲", "~b":"乙", "~c":"丙", "~d":"丁", "~e":"戊",
"~f":"己", "~g":"庚", "~h":"辛", "~i":"壬", "~j":"癸",
"_a":"子", "_b":"丑", "_c":"寅", "_d":"卯", "_e":"辰",
"_f":"巳", "_g":"午", "_h":"未", "_i":"申", "_j":"酉",
"_k":"戌", "_l":"亥",
"@a":"\u84ec","@b":"\u4efb","@c":"\u885d","@d":"\u8f14","@e":"\u82f1",
"@f":"\u82ae","@g":"\u67f1","@h":"\u5fc3","@i":"\u79bd",
"#a":"\u4f11", "#b":"\u751f", "#c":"\u50b7", "#d":"\u675c",
"#e":"\u666f", "#f":"\u6b7b", "#g":"\u9a5a", "#h":"\u958b",
"$a":"\u7b26", "$b":"\u86c7", "$c":"\u9670", "$d":"\u5408",
"$e":"\u767d", "$f":"\u7384", "$g":"\u5730", "$h":"\u5929",
"?g":"\uacf5", "?n":""
}


def get_ipchun_date(year):
    """get_ipchun_date(year) -> tuple
    Return target year ipchun date.
    - 'year' is an integer such as 2007
    - Returned tuple is like (2007, 4, 3, 2, 7). It is solar date.
    """
    #Just try to get minutes from real ipchun date to target year's August first
    tmin = mytime.get_mins_from_timedelta((1996,2,4,22,8),(year,8,1,12,00))
    tyear = tmin//525949
    ipchun_date = mytime.get_date_after_mins(tyear*525949,(1996,2,4,22,8))

    return ipchun_date


def get_dongji_date(year):
    """get_dongji_date(year) -> tuple
    Return target year ipchun date.
    - 'year' is an integer such as 2007
    - Returned tuple is like (2007, 4, 3, 2, 7). It is solar date.
    """
    ipchun_date = get_ipchun_date(year)
    dongji_date = mytime.get_date_after_mins(462295,ipchun_date)

    return dongji_date


def get_jeolki_date_list(year):
    """get_jeolki_date_list(year) -> list
    Return target year jeolki date list.
    - 'year' is an integer such as 2007
    - Returned tuple is like ((2007, 2, 4, 2, 7),(2007, 2, 15, 12,19),...,). It is solar date tuple.
    """
    global JEOLKI_GAP_FROM_IPCHUN
    result = []
    ipchun_date = get_ipchun_date(year)
    for gap in JEOLKI_GAP_FROM_IPCHUN:
        result.append(mytime.get_date_after_mins(gap,ipchun_date))

    return result


def get_jeolki_index(otime):
    """get_jeolki_index(otime) -> integer
    Return jeolki index otime belongs to.
    - 'otime' is a tuple like (2007,6,4,11,59). it should be solar date.
    - Returned integer is an index. For example, ipchun is indexed by 0.
    """
    global JEOLKI_GAP_FROM_IPCHUN

    if len(otime) != 5:
        raise TimeTypeError("Invalid input. It should be a tuple like (2007,6,4,11,59).")
        return

    otime_ipchun = get_ipchun_date(otime[0])
    if mytime.isEarlier(otime_ipchun,otime):
        min_from_ipchun = mytime.get_mins_from_timedelta(otime_ipchun,otime)
    else:
        min_from_ipchun = \
        mytime.get_mins_from_timedelta(get_ipchun_date(otime[0]-1),otime)

    jeolki_index = -1
    for j in JEOLKI_GAP_FROM_IPCHUN:
        if min_from_ipchun >= j:
            jeolki_index += 1
        else:
            break

    return jeolki_index


def get_current_jeolki_index():
    """get_current_jeolki_index() -> integer
    Return current jeolki index.
    - Returned tuple is like ('aa',ab',cd',cb')
    """
    otime = time.localtime()[:5]
    return get_jeolki_index(otime)


def isJeolkiChanging(otime):
    """isJeolkiChanging(otime) -> boolean
    Returns True if a jeolki is changing in otime (before & after 1 hour)
    - 'otime' is a tuple like (2007,6,4,11,59). it should be solar date.
    """
    global JEOLKI_GAP_FROM_IPCHUN
    otime_ipchun = get_ipchun_date(otime[0])
    otime_ji = get_jeolki_index(otime)
    if otime_ji == 23:otime_jn = 0
    else:otime_jn = otime_ji + 1

    boundary1 = mytime.get_date_after_mins\
                (JEOLKI_GAP_FROM_IPCHUN[otime_ji] + 60,otime_ipchun)
    boundary2 = mytime.get_date_after_mins\
                (JEOLKI_GAP_FROM_IPCHUN[otime_jn] - 60,otime_ipchun)

    if mytime.isEarlier(otime,boundary1) or mytime.isEarlier(boundary2,otime):
        return True
    else:
        return False


def symbol2unicode(symbol=None):
    """symbol2unicode(symbol=None) -> unicode
    Return unicode matching given symbol.
    - 'symbol' is a string like '~a'. It should be 2 strings or 0.
    It's ok 'aa', 'bf' but if too many strings are given, it will return ''.
    If no symbol is given, it will return whole symbol2unicode dictionary.
    - Returned unicode is like u'\u7532'.
    - Programmed by herokims (2007. 6. 24.)
    """
    global SYMBOL2UNICODE_TABLE

    if symbol:
        #간지를 직접 입력하는 경우에는 변환해준다
        gan = ['a','b','c','d','e','f','g','h','i','j']
        ji = ['a','b','c','d','e','f','g','h','i','j','k','l']
        ganji = [ g + j for g in gan for j in ji]
        if symbol in ganji:
            return SYMBOL2UNICODE_TABLE['~' + symbol[0]] + \
                   SYMBOL2UNICODE_TABLE['_' + symbol[1]]

        #일반적으로 심볼은 심볼 테이블에 있는 경우에만 하나씩 변환해준다
        try: return SYMBOL2UNICODE_TABLE[symbol]
        except: return ''
    else:
        return SYMBOL2UNICODE_TABLE


def unicode2symbol(uni=None):
    """unicode2symbol(uni=None) -> string
    Return symbol matching given unicode.
    - 'uni' is a unicode like u'\u7532'. It should be 1 unicode or 0.
    Any unicode is ok but too many strings'll be igonored. It will return ''.
    If no unicode is given, it will return whole unicode2symbol dictionary.
    - Returned string is like '~a'.
    - Programmed by herokims (2007. 6. 24.)
    """
    global SYMBOL2UNICODE_TABLE

    uni2sym = dict([(v,k) for k,v in list(SYMBOL2UNICODE_TABLE.items())])

    if uni:
        #유니코드는 유니코드 테이블에 있는 경우에만 하나씩 변환해준다
        try: return uni2sym[uni]
        except: return ''
    else:
        return uni2sym


def runTest():
    print("다음은 동작테스트입니다")
    print("이번년도 입춘은 " + str(get_ipchun_date(time.localtime()[0])))
    print("이번년도 동지는 " + str(get_dongji_date(time.localtime()[0])))
    print("이번년도 절기날짜 리스트는 " + str(get_jeolki_date_list(time.localtime()[0])))


if __name__ == '__main__':
    runTest()


