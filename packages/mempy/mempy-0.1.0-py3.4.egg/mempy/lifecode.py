# *-* coding: UTF8 -*-
#==============================================================================
"""
[lifecode.py] - Mempire LifeCode module

이 모듈은 명리관련 기능을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__ver__ = '150114'
__since__ = '2006-10-01'
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


import time
from mempy import time as mytime
from mempy import ichingbase
from mempy import utils as myutils
from mempy.lib import transdate


class TimeTypeError(Exception):pass


def get_lifecode(otime):
    """get_lifecode(otime) -> tuple
    Translate otime to lifecode and return it. It regards ipchun as year's beginning.
    (If you want to get lifecode in dongji base, you could use get_lifecode_dongjibase() in the same way.)
    - 'otime' is a tuple like (2007,6,4,11,59). it should be solar date.
    - Returned tuple is like ('aa','ab','cd','cb').
    """

    GAPJA60_original = ichingbase.GAPJA60
    GAPJA60 = dict((int(key),value) for key,value in GAPJA60_original.items())
    
    JEOLKI_GAP_FROM_IPCHUN = ichingbase.JEOLKI_GAP_FROM_IPCHUN

    if len(otime) != 5:
        raise TimeTypeError("Invalid input. It should be a tuple like (2007,6,4,11,59).")
        return

    #1. Get Year-ju
    try:
        otime_lun = transdate.sol2lun(otime[0],otime[1],otime[2])
        otimelunar = transdate.lunardate(otime_lun[0],otime_lun[1],\
                                         otime_lun[2],otime_lun[3])
    except:
        raise TimeTypeError("Invalid input. It should be a tuple like (2007,6,4,11,59).")
        return

    basetime_lun = transdate.sol2lun(otime[0],8,1)
    baselunar = transdate.lunardate(basetime_lun[0],basetime_lun[1],\
                                    basetime_lun[2],basetime_lun[3])

    otime_ipchun = ichingbase.get_ipchun_date(otime[0])
    otimeganzi = otimelunar.getganzi()
    baseganzi = baselunar.getganzi()

    if mytime.isEarlier(otime_ipchun,otime):
        lifecode = (GAPJA60[baseganzi[0]],)
        min_from_ipchun = mytime.get_mins_from_timedelta(otime_ipchun,otime)
    else:
        if baseganzi[0] == 0 :
            lifecode = (GAPJA60[59],)
            min_from_ipchun = \
            mytime.get_mins_from_timedelta(ichingbase.get_ipchun_date(otime[0]-1),otime)
        else:
            lifecode = (GAPJA60[baseganzi[0]-1],)
            min_from_ipchun = \
            mytime.get_mins_from_timedelta(ichingbase.get_ipchun_date(otime[0]-1),otime)

    #2. Get Month-ju
    yeargan = lifecode[0][0]
    monthgan_pos = 0
    if yeargan == 'a' or yeargan == 'f': monthgan_pos = 2
    elif yeargan == 'b' or yeargan == 'g': monthgan_pos = 14
    elif yeargan == 'c' or yeargan == 'h': monthgan_pos = 26
    elif yeargan == 'd' or yeargan == 'i': monthgan_pos = 38
    elif yeargan == 'e' or yeargan == 'j': monthgan_pos = 50

    if JEOLKI_GAP_FROM_IPCHUN[0] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[2]:
        monthgan_pos += 0           #month1
    elif JEOLKI_GAP_FROM_IPCHUN[2] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[4]:
        monthgan_pos += 1           #month2
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[4] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[6]:
        monthgan_pos += 2           #month3
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[6] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[8]:
        monthgan_pos += 3           #month4
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[8] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[10]:
        monthgan_pos += 4           #month5
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[10] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[12]:
        monthgan_pos += 5           #month6
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[12] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[14]:
        monthgan_pos += 6           #month7
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[14] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[16]:
        monthgan_pos += 7           #month8
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[16] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[18]:
        monthgan_pos += 8           #month9
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[18] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[20]:
        monthgan_pos += 9           #month10
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[20] <= min_from_ipchun < JEOLKI_GAP_FROM_IPCHUN[22]:
        monthgan_pos += 10          #month11
        if monthgan_pos > 59: monthgan_pos -= 60
    elif JEOLKI_GAP_FROM_IPCHUN[22] <= min_from_ipchun:
        monthgan_pos += 11          #month12
        if monthgan_pos > 59: monthgan_pos -= 60
    lifecode += (GAPJA60[monthgan_pos],)

    #3. Get Day-ju (if yajasi, adjust yesterday's Day-ju)
    elapsed_min = otime[3] * 60 + otime[4] #Convert otime to elapsed minutes
    if 0 <= elapsed_min < 30:
        if otimeganzi[2] == 0 :
            lifecode += (GAPJA60[59],)
        else:
            lifecode += (GAPJA60[otimeganzi[2]-1],)
    else:
        lifecode += (GAPJA60[otimeganzi[2]],)

    #4. Get Time-ju
    #timegan is determined by daygan
    daygan = lifecode[2][0]
    timegan_pos = 0
    if daygan == 'a' or daygan == 'f': timegan_pos = 0
    elif daygan == 'b' or daygan == 'g': timegan_pos = 12
    elif daygan == 'c' or daygan == 'h': timegan_pos = 24
    elif daygan == 'd' or daygan == 'i': timegan_pos = 36
    elif daygan == 'e' or daygan == 'j': timegan_pos = 48

    if 30 <= elapsed_min < 90:timegan_pos += 0          #00:30 ~ 01:30
    elif 90 <= elapsed_min < 210:timegan_pos += 1       #01:30 ~ 03:30
    elif 210 <= elapsed_min < 330:timegan_pos += 2      #03:30 ~ 05:30
    elif 330 <= elapsed_min < 450:timegan_pos += 3      #05:30 ~ 07:30
    elif 450 <= elapsed_min < 570:timegan_pos += 4      #07:30 ~ 09:30
    elif 570 <= elapsed_min < 690:timegan_pos += 5      #09:30 ~ 11:30
    elif 690 <= elapsed_min < 810:timegan_pos += 6      #11:30 ~ 13:30
    elif 810 <= elapsed_min < 930:timegan_pos += 7      #13:30 ~ 15:30
    elif 930 <= elapsed_min < 1050:timegan_pos += 8     #15:30 ~ 17:30
    elif 1050 <= elapsed_min < 1170:timegan_pos += 9    #17:30 ~ 19:30
    elif 1170 <= elapsed_min < 1290:timegan_pos += 10   #19:30 ~ 21:30
    elif 1290 <= elapsed_min < 1410:timegan_pos += 11   #21:30 ~ 23:30
    #23:30 ~ 00:30 (yajasi)
    elif (1410 <= elapsed_min < 1440) or (0 <= elapsed_min < 30):
        #if yajasi, adjust next day's ja-si
        timegan_pos += 12
        if timegan_pos == 60 : timegan_pos = 0

    #append timeju
    lifecode += (GAPJA60[timegan_pos],)

    return lifecode


def get_lifecode_dongjibase(otime):
    """get_lifecode_dongjibase(otime) -> tuple
    Translate otime to lifecode and return it. It regard dongji as year's beginning.
    - 'otime' is a tuple like (2007,6,4,11,59). it should be solar date.
    - Returned tuple is like ('aa','ab','cd','cb').
    """

    GAPJA60_original = ichingbase.GAPJA60
    GAPJA60 = dict((int(key),value) for key,value in GAPJA60_original.items())

    #동지를 기준으로 하는 사주를 구하기 위해서는
    #기존 방식(입춘기준)으로 일단 사주를 구했다가,
    #동지부터 입춘사이의 연주만 그 다음 간지의 연주로 바꾸기만 하면 된다.
    olifecode = get_lifecode(otime)
    dongji_date = ichingbase.get_dongji_date(otime[0])

    basetime_lun = transdate.sol2lun(otime[0],8,1)
    baselunar = transdate.lunardate(basetime_lun[0],basetime_lun[1],\
                                    basetime_lun[2],basetime_lun[3])
    baseganzi = baselunar.getganzi()

    #1. Get Year-ju
    if mytime.isEarlier(dongji_date,otime):
        if baseganzi[0] == 59 :
            new_yearju = GAPJA60[0]
        else:
            new_yearju = GAPJA60[baseganzi[0]+1]
    else:
        new_yearju = GAPJA60[baseganzi[0]]

    olifecode = list(olifecode)
    olifecode[0] = new_yearju
    olifecode = tuple(olifecode)

    return olifecode


def get_current_lifecode():
    """get_current_lifecode() -> tuple
    Translate current time to lifecode and return it.
    - Returned tuple is like ('aa',ab',cd',cb')
    """
    otime = time.localtime()[:5]
    return get_lifecode(otime)


def translate(lcode):
    """translate() -> tuple
    Translate lifecode code(ex. aa, bd, bc, df) to real hanja
    - Returned tuple is like ('甲子','丙戌','庚午','壬午')
    """
    
    GAPJA60 = ichingbase.GAPJA60
    GAPJA60h = ichingbase.GAPJA60h
    GAPJA60r = myutils.reverseDict(GAPJA60)    
    
    tcode = [GAPJA60r[ju] for ju in lcode]    
    hcode = [GAPJA60h[ju] for ju in tcode]
         
    return tuple(hcode)
    

def runTest():
    
    otime = time.localtime()[:5]
    #otime = (1977,12,13,0,20)
    
    print("지금 시간 사주(입춘기준)")
    print(str(get_lifecode(otime)))
    
    #이상하게 print(translate((get_lifecode(otime))))하면 
    #translate()함수 'tcode = ... '부분에서 에러가 난다.
    lc = translate((get_lifecode(otime)))
    print(lc)  
    
    
    print("지금 시간 사주(동지기준)")
    print(str(get_lifecode_dongjibase(otime)))
    
    #이상하게 print(translate((get_lifecode(otime))))하면 
    #translate()함수 'tcode = ... '부분에서 에러가 난다.
    lc2 = translate(get_lifecode_dongjibase(otime))    
    print(lc2)


if __name__ == '__main__':
    runTest()
    
