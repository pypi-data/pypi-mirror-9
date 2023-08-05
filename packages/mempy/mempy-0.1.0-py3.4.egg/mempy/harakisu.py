# *-* coding: UTF8 -*-
#==============================================================================
"""
[harakisu.py] - Mempire Harakisu module

이 모듈은 하락이수 이론을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__ver__ = '150114'
__since__ = '2006-10-01' #translated to Python in 2007. 6. 23. 15:54 ~ 20:55
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


import time
from mempy import time as mytime
from mempy import ichingbase
from mempy import lifecode


class TimeTypeError(Exception):pass


def isYanggan(gan_str):
    """isYanggan(gan_str) -> boolean
    Return true if given gan_str is Yanggan.
    - 'gan_str' is a string like 'a'. it should be a Real gan symbol('a' to 'j').
    - Programmed by herokims (2006. 10. 25.) and translated to Python in 2007. 6. 23.
    """
    if gan_str in ('a','c','e','g','i'):
        return True
    else:
        return False


def isyangsi(ji_str):
    """isyangsi(ji_str) -> boolean
    Return true if given ji_str is yangsi.
    - 'ji_str' is a string like 'a'. it should be a Real ji symbol('a' to 'l').
    - Programmed by herokims (2006. 10. 25.) and translated to Python in 2007. 6. 23.
    """
    if ji_str in ('a','b','c','d','e','f'):
        return True
    else:
        return False
    

def _mark_wondanghyo(goe,isYanghyo,hyo_nth_pos):
    """_mark_wondanghyo(goe,isYanghyo,hyo_nth_pos) -> string
    입력되는 괘에 원당효를 표시하여 반환한다.
    - 'goe' is a string like '333233'.
    - 'isYanghyo' is boolean like True.
    - 'hyo_nth_pos' is integer like 3. It means how nth times hyo will be changed.
    And it ranges from 1 to 6(CAUTION: Not 0).
    - Returned string is like '933233'.
    - Programmed by herokims (2006. 10. 26) and translated to Python in 2007. 6. 23.
    """
    
    #이미 동효가 표시되어 있다면 일단 표시를 지운다
    goe = goe.replace('6', '2')
    goe = goe.replace('9', '3')
    
    if isYanghyo:
        cnt = 0
        for intx in range(1,7):
            if goe[intx-1] == '3':
                cnt += 1
                if cnt == hyo_nth_pos:
                    goe = list(goe)
                    goe[intx-1] = '9'
                    goe = "".join(goe)
                    return goe
    else:
        cnt = 0
        for intx in range(1,7):
            if goe[intx-1] == '2':
                cnt += 1
                if cnt == hyo_nth_pos:
                    goe = list(goe)
                    goe[intx-1] = '6'
                    goe = "".join(goe)
                    return goe


def _reverse_hyo(goe,hyo_pos,isDong,isOnedong):
    """_reverse_hyo(goe,hyo_pos,isDong,isOnedong) -> string
    입력되는 괘의 지정한 위치 효를 바꾼다.
    - 'goe' is a string like '333233'.
    - 'hyo_pos' is 바꿀 효의 위치
    - 'isDong' is 그 효를 동효(6,9)로 표시할 것인지 여부
    - 'isOnedong' is 동효는 한개만 표시할 것인지 여부
    - Returned string is like '933233'.
    - 만약 isOneDong에 True할 경우, 기존에 표시된 동효는 2,3으로 전환되고, 새로운 동효만 표시된다
    - Programmed by herokims (2006. 10. 26) and translated to Python in 2007. 6. 23.
    """

    if isOnedong:
        goe = goe.replace('6', '2')
        goe = goe.replace('9', '3')
    
    if isDong:
        if goe[hyo_pos-1] in ('2','6'):
            goe = list(goe)
            goe[hyo_pos-1] = '9'
            goe = "".join(goe)
        elif goe[hyo_pos-1] in ('3','9'):
            goe = list(goe)
            goe[hyo_pos-1] = '6'
            goe = "".join(goe)
    else:
        if goe[hyo_pos-1] in ('2','6'):
            goe = list(goe)
            goe[hyo_pos-1] = '3'
            goe = "".join(goe)
        elif goe[hyo_pos-1] in ('3','9'):
            goe = list(goe)
            goe[hyo_pos-1] = '2'
            goe = "".join(goe)
    
    return goe


def get_harakisu(otime,gender):
    """(-> tuple) : 하락이수 '본괘'와 관련 정보 반환.
    
    - 'otime'는 (2007,6,4,11,59) 형태의 tuple. 반드시 양력이어야 함.
    - 'gender'는 integer 타입. 1은 남성, 2는 여성.
    - 반환되는 tuple의 구조는 (선천괘,후천괘,
      천수합,지수합,원기,반원기,납갑,화공,반화공,득체,득시)로 되어 있음.
    - ex. ('333923', '623333', 34, 36, ['333', '323'], ['222', '232'], [0, 0], '232', '323', ['223', '323', '222'], [False, False])
    - 참고로 이 모듈에서 사용하는 괘모양은 123456 형태로, 왼쪽부터 초효가 시작되며,
    - '3' 는 소양, '2'는 소음, '6'은 노음, '9'는 노양을 의미함.
    - 원기, 반원기, 납갑, 득체, 득시는 ListType.
    - 납갑, 득시는 2 Item으로 구성. (처음 Item은 선천괘, 둘째 Item은 후천괘)
    - 납갑은 0, 1, 2 중 하나. 
      '0' 은 '납갑없음', '1' 은 '납갑있음', '2' 는 '납갑차용'
    - Programmed by herokims (2006. 10. 25. ~ 30. Version 2.0.0)
    - Function Added in 2007. 8. 31. 16:00 ~ 19:50
    """
    
    bornyear = otime[0]
    lcode = lifecode.get_lifecode(otime)
    yeargan = lcode[0][0]
    timeji = lcode[3][1]
    isYangwol = None
    if isYanggan(lcode[1][0]): isYangwol = True
    else: isYangwol = False
    
    #원기리스트를 구한다
    wongi = []; banwongi = []
    if (lcode[0][0] in ['a','i']) or (lcode[0][1] in ['k','l']):
        wongi.append('333'); banwongi.append('222')
    if (lcode[0][0] in ['e']) or (lcode[0][1] in ['a']):
        wongi.append('232'); banwongi.append('323')
    if (lcode[0][0] in ['c']) or (lcode[0][1] in ['b','c']):
        wongi.append('223'); banwongi.append('332')
    if (lcode[0][0] in ['g']) or (lcode[0][1] in ['d']):
        wongi.append('322'); banwongi.append('233')
    if (lcode[0][0] in ['h']) or (lcode[0][1] in ['e','f']):
        wongi.append('233'); banwongi.append('322')
    if (lcode[0][0] in ['f']) or (lcode[0][1] in ['g']):
        wongi.append('323'); banwongi.append('232')
    if (lcode[0][0] in ['b','j']) or (lcode[0][1] in ['h','i']):
        wongi.append('222'); banwongi.append('333')
    if (lcode[0][0] in ['d']) or (lcode[0][1] in ['j']):
        wongi.append('332'); banwongi.append('223')
    
    #화공을 구한다
    hwagong = ''; banhwagong = ''
    jeolki_index = ichingbase.get_jeolki_index(otime)
    #춘분부터 망종까지
    if 3 <= jeolki_index <= 8 : hwagong = '322'; banhwagong = '233'
    #하지부터 백로까지
    elif 9 <= jeolki_index <= 14 : hwagong = '323'; banhwagong = '232'
    #추분부터 대설까지
    elif 15 <= jeolki_index <= 20 : hwagong = '332'; banhwagong = '223'
    #동지부터 경칩까지
    elif (21 <= jeolki_index) or (jeolki_index <= 2) : hwagong = '232'; banhwagong = '323'
    
    otime_9 = mytime.get_date_after_mins(12960, otime)
    otime_18 = mytime.get_date_after_mins(25920, otime)
    jeolki_9 = ichingbase.get_jeolki_index(otime_9)
    jeolki_18 = ichingbase.get_jeolki_index(otime_18)
    
    if jeolki_index != 0 and jeolki_18 == 0 and jeolki_9 != 0:
        hwagong = '222'; banhwagong = '333'
    elif jeolki_index != 0 and jeolki_9 == 0:
        hwagong = '223'; banhwagong = '332'
        
    if jeolki_index != 6 and jeolki_18 == 6 and jeolki_9 != 6:
        hwagong = '222'; banhwagong = '333'
    elif jeolki_index != 6 and jeolki_9 == 6:
        hwagong = '223'; banhwagong = '332'
        
    if jeolki_index != 12 and jeolki_18 == 12 and jeolki_9 != 12:
        hwagong = '222'; banhwagong = '333'
    elif jeolki_index != 12 and jeolki_9 == 12:
        hwagong = '223'; banhwagong = '332'
        
    if jeolki_index != 18 and jeolki_18 == 18 and jeolki_9 != 18:
        hwagong = '222'; banhwagong = '333'
    elif jeolki_index != 18 and jeolki_9 == 18:
        hwagong = '223'; banhwagong = '332'
    
    #득체를 구한다
    getche = []
    if lcode[2][0] in ['a','b']: getche = ['232','223','322']
    elif lcode[2][0] in ['c','d']: getche = ['333','233','222']
    elif lcode[2][0] in ['e','f']: getche = ['223','323','222']
    elif lcode[2][0] in ['g','h']: getche = ['333','322','222','332']
    elif lcode[2][0] in ['i','j']: getche = ['333','222','332']
    
    #천간취수정국(낙서기준), 지지취수정국(하도기준)
    jisu = 0; cheonsu = 0
    for ju in lcode:
        #천간취수정국 처리
        if ju[0] == 'a': jisu += 6
        elif ju[0] == 'b': jisu += 2
        elif ju[0] == 'c': jisu += 8
        elif ju[0] == 'd': cheonsu += 7
        elif ju[0] == 'e': cheonsu += 1
        elif ju[0] == 'f': cheonsu += 9
        elif ju[0] == 'g': cheonsu += 3
        elif ju[0] == 'h': jisu += 4
        elif ju[0] == 'i': jisu += 6
        elif ju[0] == 'j': jisu += 2
        else: pass
        #지지취수정국 처리
        if ju[1] == 'a': cheonsu += 1; jisu += 6
        elif ju[1] == 'b': cheonsu += 5; jisu += 10
        elif ju[1] == 'c': cheonsu += 3; jisu += 8
        elif ju[1] == 'd': cheonsu += 3; jisu += 8
        elif ju[1] == 'e': cheonsu += 5; jisu += 10
        elif ju[1] == 'f': cheonsu += 7; jisu += 2
        elif ju[1] == 'g': cheonsu += 7; jisu += 2
        elif ju[1] == 'h': cheonsu += 5; jisu += 10
        elif ju[1] == 'i': cheonsu += 9; jisu += 4
        elif ju[1] == 'j': cheonsu += 9; jisu += 4
        elif ju[1] == 'k': cheonsu += 5; jisu += 10
        elif ju[1] == 'l': cheonsu += 1; jisu += 6
        else: pass
    
    cheonsu_sum = cheonsu
    jisu_sum = jisu
    
    #천수, 지수를 먼저 공식수(천수는 25, 지수는 30)로 제한 뒤,
    #나머지를 얻어 소성괘를 구하되(이때 소성괘순서가 아닌 구궁방식임)
    #만약 천수,지수가 공식수를 넘지 않으면 10단위로 뺀다.
    #천수괘수, 지수괘수가 10의 배수일 경우, 10은 사용하지 않으므로 앞자리만 사용한다
    
    #천수합이 25를 넘는 경우
    if cheonsu > 25:
        cheonsu = cheonsu - 25
        if cheonsu == 10:
            cheonsu_goesu = 1
        elif cheonsu == 20:
            cheonsu_goesu = 2
        elif cheonsu == 30:
            cheonsu_goesu = 3  
        #천수가 10또는 20 또는 30이 아니면 10으로 나눈 나머지를 취한다
        else:
            cheonsu_goesu = divmod(cheonsu,10)[1]
    #천수합이 25인 경우
    elif cheonsu == 25:
        cheonsu_goesu = 5 #나중에 일괄 처리하기 위해 일단 나머지 5를 그대로 둔다.
    #천수합이 25미만인 경우
    else:
        if cheonsu == 10:
            cheonsu_goesu = 1
        elif cheonsu == 20:
            cheonsu_goesu = 2
        else:
            cheonsu_goesu = divmod(cheonsu,10)[1]
    
    #지수합이 60인 경우
    if jisu == 60:
        jisu_goesu = 3
    #지수합이 30보다 크고 60보다 작은 경우
    elif 30 < jisu < 60:
        jisu = jisu - 30
        if jisu == 10:
            jisu_goesu = 1
        elif jisu == 20:
            jisu_goesu = 2
        elif jisu == 30:
            jisu_goesu = 3
        #지수가 10또는 20 또는 30이 아니면 10으로 나눈 나머지를 취한다
        else:
            jisu_goesu = divmod(jisu,10)[1]
    elif jisu == 30:
        jisu_goesu = 3
    #지수합이 30미만인 경우
    else:
        if jisu == 10:
            jisu_goesu = 1
        elif jisu == 20:
            jisu_goesu = 2
        else:
            jisu_goesu = divmod(jisu,10)[1]
    
    #천수에서 나머지가 5인 경우 처리
    if cheonsu_goesu == 5:
        if 1864 <= otime[0] <= 1923:
            if gender == 1:
                cheonsu_goesu = 8
            else:
                cheonsu_goesu = 2
        elif 1924 <= otime[0] <= 1983:
            #양남
            if isYanggan(lcode[0]) and gender == 1:
               cheonsu_goesu = 8
            #음녀
            elif not isYanggan(lcode[0]) and gender == 2:
                cheonsu_goesu = 8
            #음남, 양녀
            else:
                cheonsu_goesu = 2
        elif otime[0] >= 1984:
            if gender == 1:
                cheonsu_goesu = 9
            else:
                cheonsu_goesu = 7

    #지수에서 나머지가 5인 경우 처리
    if jisu_goesu == 5:
        if 1864 <= otime[0] <= 1923:
            if gender == 1:
                jisu_goesu = 8
            else:
                jisu_goesu = 2
        elif 1924 <= otime[0] <= 1983:
            #양남
            if isYanggan(lcode[0]) and gender == 1:
               jisu_goesu = 8
            #음녀
            elif not isYanggan(lcode[0]) and gender == 2:
                jisu_goesu = 8
            #음남, 양녀
            else:
                jisu_goesu = 2
        elif otime[0] >= 1984:
            if gender == 1:
                jisu_goesu = 9
            else:
                jisu_goesu = 7

    #이렇게 구해진 천수괘수, 지수괘수로 천수괘, 지수괘를 구한다(낙서배열에 따름)
    if cheonsu_goesu == 1: c_goe = '232'     
    elif cheonsu_goesu == 2: c_goe = '222'   
    elif cheonsu_goesu == 3: c_goe = '322'  
    elif cheonsu_goesu == 4: c_goe = '233'  
    elif cheonsu_goesu == 5:
        if 1864 <= bornyear <= 1923:
            if gender == 1: c_goe = '223'   
            elif gender == 2: c_goe = '222' 
            else: pass
        elif 1924 <= bornyear <= 1983:
            if gender == 1:
                if isYanggan(yeargan): c_goe = '223'    
                else: c_goe = '222'                     
            else:
                if isYanggan(yeargan): c_goe = '222'    
                else: c_goe = '223'                     
        elif 1984 <= bornyear <= 2043:
            if gender == 1: c_goe = '323'   
            else: c_goe = '332'             
    elif cheonsu_goesu == 6: c_goe = '333'
    elif cheonsu_goesu == 7: c_goe = '332'  
    elif cheonsu_goesu == 8: c_goe = '223'
    elif cheonsu_goesu == 9: c_goe = '323'
    
    if jisu_goesu == 1: j_goe = '232'
    elif jisu_goesu == 2: j_goe = '222'
    elif jisu_goesu == 3: j_goe = '322'
    elif jisu_goesu == 4: j_goe = '233'
    elif jisu_goesu == 5:
        if 1864 <= bornyear <= 1923:
            if gender == 1: j_goe = '223'   
            elif gender == 2: j_goe = '222' 
            else: pass
        elif 1924 <= bornyear <= 1983:
            if gender == 1:
                if isYanggan(yeargan): j_goe = '223'    
                else: j_goe = '222'                     
            else:
                if isYanggan(yeargan): j_goe = '222'    
                else: j_goe = '223'                     
        elif 1984 <= bornyear <= 2043:
            if gender == 1: j_goe = '323'   
            else: j_goe = '332'             
    elif jisu_goesu == 6: j_goe = '333'
    elif jisu_goesu == 7: j_goe = '332'  
    elif jisu_goesu == 8: j_goe = '223'
    elif jisu_goesu == 9: j_goe = '323'  
        
    #양남과 음녀의 경우, 천수괘는 외괘, 지수괘는 내괘로 배치하고
    firstgoe = ""; lastgoe = ""
    if ((gender == 1) and isYanggan(yeargan)) or \
        ((gender == 2) and not isYanggan(yeargan)):
        firstgoe = str(j_goe) + str(c_goe)
    else:
        firstgoe = str(c_goe) + str(j_goe)
    
    firstgoe = str(firstgoe)
    
    #선천괘에서 양효가 몇개있는지 센다
    cnt = 0
    cnt = firstgoe.count('3')
    intx = cnt
    
    #괘의 종류에 따라 각각의 방식으로 원당효를 구한다 (intX는 양효의 개수)
    if intx == 1:
    
        #1양효괘(5음효괘)에서 양시생의 경우
        if isyangsi(timeji):
            #자, 축시생은 첫번째 양효가 원당효이다
            if timeji in ('a','b'): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            #인시생은 첫번째 음효가 원당효이다
            elif timeji in ('c',): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('d',): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('e',): firstgoe = _mark_wondanghyo(firstgoe,False,3)
            elif timeji in ('f',): firstgoe = _mark_wondanghyo(firstgoe,False,4)
                        
        #1양효괘(5음효괘)에서 음시생의 경우
        else:
            if timeji in ('g',): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('h',): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('i',): firstgoe = _mark_wondanghyo(firstgoe,False,3)
            elif timeji in ('j',): firstgoe = _mark_wondanghyo(firstgoe,False,4)
            elif timeji in ('k',): firstgoe = _mark_wondanghyo(firstgoe,False,5)
            elif timeji in ('l',): firstgoe = _mark_wondanghyo(firstgoe,True,1)
    
    elif intx == 2:

        #2양효괘(4음효괘)에서 양시생의 경우
        if isyangsi(timeji):
            if timeji in ('a','c'): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('b','d'): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('e',): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('f',): firstgoe = _mark_wondanghyo(firstgoe,False,2)
                        
        #2양효괘(4음효괘)에서 음시생의 경우
        else:
            if timeji in ('g',): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('h',): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('i',): firstgoe = _mark_wondanghyo(firstgoe,False,3)
            elif timeji in ('j',): firstgoe = _mark_wondanghyo(firstgoe,False,4)
            elif timeji in ('k',): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('l',): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            
    elif intx == 3:

        #3양효괘(3음효괘)에서 양시생의 경우
        if isyangsi(timeji):
            if timeji in ('a','d'): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('b','e'): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('c','f'): firstgoe = _mark_wondanghyo(firstgoe,True,3)
                        
        #3양효괘(3음효괘)에서 음시생의 경우
        else:
            if timeji in ('g','j'): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('h','k'): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('i','l'): firstgoe = _mark_wondanghyo(firstgoe,False,3)

    elif intx == 4:

        #4양효괘(2음효괘)에서 양시생의 경우
        if isyangsi(timeji):
            if timeji in ('a',): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('b',): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('c',): firstgoe = _mark_wondanghyo(firstgoe,True,3)
            elif timeji in ('d',): firstgoe = _mark_wondanghyo(firstgoe,True,4)
            elif timeji in ('e',): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('f',): firstgoe = _mark_wondanghyo(firstgoe,False,2)
                        
        #4양효괘(2음효괘)에서 음시생의 경우
        else:
            if timeji in ('g','i'): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('h','j'): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('k',): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('l',): firstgoe = _mark_wondanghyo(firstgoe,True,2)

    elif intx == 5:

        #5양효괘(1음효괘)에서 양시생의 경우
        if isyangsi(timeji):
            if timeji in ('a',): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('b',): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('c',): firstgoe = _mark_wondanghyo(firstgoe,True,3)
            elif timeji in ('d',): firstgoe = _mark_wondanghyo(firstgoe,True,4)
            elif timeji in ('e',): firstgoe = _mark_wondanghyo(firstgoe,True,5)
            elif timeji in ('f',): firstgoe = _mark_wondanghyo(firstgoe,False,1)
                        
        #5양효괘(1음효괘)에서 음시생의 경우
        else:
            if timeji in ('g','h'): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('i',): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('j',): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('k',): firstgoe = _mark_wondanghyo(firstgoe,True,3)
            elif timeji in ('l',): firstgoe = _mark_wondanghyo(firstgoe,True,4)
        
    elif intx == 6:

        #순양효괘에서 남자가 양시생인 경우
        if (gender == 1) and isyangsi(timeji):
            if timeji in ('a','d'): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('b','e'): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('c','f'): firstgoe = _mark_wondanghyo(firstgoe,True,3)
        #순양효괘에서 남자가 음시생인 경우
        elif (gender == 1) and not isyangsi(timeji):
            if timeji in ('g','j'): firstgoe = _mark_wondanghyo(firstgoe,True,4)
            elif timeji in ('h','k'): firstgoe = _mark_wondanghyo(firstgoe,True,5)
            elif timeji in ('i','l'): firstgoe = _mark_wondanghyo(firstgoe,True,6)
        #순양효괘에서 여자가 양월생이고 양시생인 경우
        elif (gender == 2) and isYangwol and isyangsi(timeji):
            if timeji in ('a','d'): firstgoe = _mark_wondanghyo(firstgoe,True,6)
            elif timeji in ('b','e'): firstgoe = _mark_wondanghyo(firstgoe,True,5)
            elif timeji in ('c','f'): firstgoe = _mark_wondanghyo(firstgoe,True,4)          
        #순양효괘에서 여자가 양월생이고 음시생인 경우
        elif (gender == 2) and isYangwol and not isyangsi(timeji):
            if timeji in ('g','j'): firstgoe = _mark_wondanghyo(firstgoe,True,3)
            elif timeji in ('h','k'): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('i','l'): firstgoe = _mark_wondanghyo(firstgoe,True,1)     
        #순양효괘에서 여자가 음월생이고 양시생인 경우(남자와 동일)
        elif (gender == 2) and not isYangwol and isyangsi(timeji):
            if timeji in ('a','d'): firstgoe = _mark_wondanghyo(firstgoe,True,1)
            elif timeji in ('b','e'): firstgoe = _mark_wondanghyo(firstgoe,True,2)
            elif timeji in ('c','f'): firstgoe = _mark_wondanghyo(firstgoe,True,3)
        #순양효괘에서 여자가 음월생이고 음시생인 경우(남자와 동일)
        elif (gender == 2) and not isYangwol and not isyangsi(timeji):
            if timeji in ('g','j'): firstgoe = _mark_wondanghyo(firstgoe,True,4)
            elif timeji in ('h','k'): firstgoe = _mark_wondanghyo(firstgoe,True,5)
            elif timeji in ('i','l'): firstgoe = _mark_wondanghyo(firstgoe,True,6)

    elif intx == 0:

        #순음효괘에서 여자가 양시생인 경우
        if (gender == 2) and isyangsi(timeji):
            if timeji in ('a','d'): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('b','e'): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('c','f'): firstgoe = _mark_wondanghyo(firstgoe,False,3)
        #순음효괘에서 여자가 음시생인 경우
        elif (gender == 2) and not isyangsi(timeji):
            if timeji in ('g','j'): firstgoe = _mark_wondanghyo(firstgoe,False,4)
            elif timeji in ('h','k'): firstgoe = _mark_wondanghyo(firstgoe,False,5)
            elif timeji in ('i','l'): firstgoe = _mark_wondanghyo(firstgoe,False,6)
        #순음효괘에서 남자가 음월생이고 양시생인 경우
        elif (gender == 1) and not isYangwol and isyangsi(timeji):
            if timeji in ('a','d'): firstgoe = _mark_wondanghyo(firstgoe,False,6)
            elif timeji in ('b','e'): firstgoe = _mark_wondanghyo(firstgoe,False,5)
            elif timeji in ('c','f'): firstgoe = _mark_wondanghyo(firstgoe,False,4)          
        #순음효괘에서 남자가 음월생이고 음시생인 경우
        elif (gender == 1) and not isYangwol and not isyangsi(timeji):
            if timeji in ('g','j'): firstgoe = _mark_wondanghyo(firstgoe,False,3)
            elif timeji in ('h','k'): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('i','l'): firstgoe = _mark_wondanghyo(firstgoe,False,1)     
        #순음효괘에서 남자가 양월생이고 양시생인 경우(여자와 동일)
        elif (gender == 1) and isYangwol and isyangsi(timeji):
            if timeji in ('a','d'): firstgoe = _mark_wondanghyo(firstgoe,False,1)
            elif timeji in ('b','e'): firstgoe = _mark_wondanghyo(firstgoe,False,2)
            elif timeji in ('c','f'): firstgoe = _mark_wondanghyo(firstgoe,False,3)
        #순음효괘에서 남자가 양월생이고 음시생인 경우(여자와 동일)
        elif (gender == 1) and isYangwol and not isyangsi(timeji):
            if timeji in ('g','j'): firstgoe = _mark_wondanghyo(firstgoe,False,4)
            elif timeji in ('h','k'): firstgoe = _mark_wondanghyo(firstgoe,False,5)
            elif timeji in ('i','l'): firstgoe = _mark_wondanghyo(firstgoe,False,6)
        else:
            #이부분은 나오지 않는 것으로 이미 검증됨
            pass

    strtemp = ''
    strtemp = firstgoe
    tempgoe = firstgoe
    in_goe = ''; out_goe = ''
    
    strtemp = strtemp.replace('6','2')
    strtemp = strtemp.replace('9','3')

    #만약 3지존괘(감위수, 수산건, 수뢰둔괘)일 경우는 양월여부에 따라 후천괘로 변환한다
    if (strtemp == '232232') or (strtemp == '223232') or (strtemp == '322232'):
        #만약 원당효가 '구오'이고 음월생이면 괘는 변하되, 효는 바꾸지 않는다
        if tempgoe[4] == '9' and not isYangwol:
            in_goe = tempgoe[0:3]; out_goe = tempgoe[3:]
            lastgoe = out_goe + in_goe
        #만약 원당효가 '구오'이고 양월생이면 괘와 효가 모두 변한다
        elif tempgoe[4] == '9' and isYangwol:
            tempgoe = tempgoe.replace('9','6')
            in_goe = tempgoe[0:3]; out_goe = tempgoe[3:]
            lastgoe = out_goe + in_goe
        #만약 원당효가 '상육'이고 음월생이면 괘와 효가 모두 변한다
        elif tempgoe[5] == '6' and not isYangwol:
            tempgoe = tempgoe.replace('6','9')
            in_goe = tempgoe[0:3]; out_goe = tempgoe[3:]
            lastgoe = out_goe + in_goe
        #만약 원당효가 '상육'이고 양월생이면 괘는 변하되, 효는 바꾸지 않는다
        elif tempgoe[5] == '6' and isYangwol:
            in_goe = tempgoe[0:3]; out_goe = tempgoe[3:]
            lastgoe = out_goe + in_goe
        #그 외는 3지존괘라 하더라도 일반적인 변환을 한다
        else:
            if '6' in tempgoe: tempgoe = tempgoe.replace('6','9')
            elif '9' in tempgoe: tempgoe = tempgoe.replace('9','6')
            in_goe = tempgoe[0:3]; out_goe = tempgoe[3:]
            lastgoe = out_goe + in_goe
            
    #그 이외의 괘는 일반적인 변환을 한다
    else:
        if '6' in tempgoe: tempgoe = tempgoe.replace('6','9')
        elif '9' in tempgoe: tempgoe = tempgoe.replace('9','6')
        
        in_goe = tempgoe[0:3]; out_goe = tempgoe[3:]
        
        #후천괘는 원당효가 바뀌고 내괘와 외괘의 위치가 바뀌는 방식으로 변환된다
        lastgoe = out_goe + in_goe

    fgoe_net = firstgoe
    fgoe_net.replace('6','2')
    fgoe_net.replace('9','3')
    lgoe_net = lastgoe
    lgoe_net.replace('6','2')
    lgoe_net.replace('9','3')

    #납갑여부를 구한다(0:없음, 1:있음, 2:차용).
    napgap = [0,0]
    if lcode[0] in ['ik','ii','ig']:
        if fgoe_net[3:] == '333': napgap[0] = 1
        elif fgoe_net[:3] == '333': napgap[0] = 2
    if lcode[0] in ['ae','ac','aa']:
        if fgoe_net[3:] == '333': napgap[0] = 2
        elif fgoe_net[:3] == '333': napgap[0] = 1
        
    if lcode[0] in ['ea','ek','ei']:
        if fgoe_net[3:] == '232': napgap[0] = 1
        elif fgoe_net[:3] == '232': napgap[0] = 2
    if lcode[0] in ['eg','ee','ec']:
        if fgoe_net[3:] == '232': napgap[0] = 2
        elif fgoe_net[:3] == '232': napgap[0] = 1

    if lcode[0] in ['cc','ca','ck']:
        if fgoe_net[3:] == '223': napgap[0] = 1
        elif fgoe_net[:3] == '223': napgap[0] = 2
    if lcode[0] in ['ci','cg','ce']:
        if fgoe_net[3:] == '223': napgap[0] = 2
        elif fgoe_net[:3] == '223': napgap[0] = 1

    if lcode[0] in ['gk','gi','gg']:
        if fgoe_net[3:] == '322': napgap[0] = 1
        elif fgoe_net[:3] == '322': napgap[0] = 2
    if lcode[0] in ['ge','gc','ga']:
        if fgoe_net[3:] == '322': napgap[0] = 2
        elif fgoe_net[:3] == '322': napgap[0] = 1

    if lcode[0] in ['hd','hf','hh']:
        if fgoe_net[3:] == '233': napgap[0] = 1
        elif fgoe_net[:3] == '233': napgap[0] = 2
    if lcode[0] in ['hj','hl','hb']:
        if fgoe_net[3:] == '233': napgap[0] = 2
        elif fgoe_net[:3] == '233': napgap[0] = 1

    if lcode[0] in ['ff','fh','fj']:
        if fgoe_net[3:] == '323': napgap[0] = 1
        elif fgoe_net[:3] == '323': napgap[0] = 2
    if lcode[0] in ['fl','fb','fd']:
        if fgoe_net[3:] == '323': napgap[0] = 2
        elif fgoe_net[:3] == '323': napgap[0] = 1 

    if lcode[0] in ['jj','jl','jb']:
        if fgoe_net[3:] == '222': napgap[0] = 1
        elif fgoe_net[:3] == '222': napgap[0] = 2
    if lcode[0] in ['bd','bf','bh']:
        if fgoe_net[3:] == '222': napgap[0] = 2
        elif fgoe_net[:3] == '222': napgap[0] = 1

    if lcode[0] in ['dh','dj','dl']:
        if fgoe_net[3:] == '332': napgap[0] = 1
        elif fgoe_net[:3] == '332': napgap[0] = 2
    if lcode[0] in ['db','dd','df']:
        if fgoe_net[3:] == '332': napgap[0] = 2
        elif fgoe_net[:3] == '332': napgap[0] = 1
        
    if lcode[0] in ['ik','ii','ig']:
        if lgoe_net[3:] == '333': napgap[1] = 1
        elif lgoe_net[:3] == '333': napgap[1] = 2
    if lcode[0] in ['ae','ac','aa']:
        if lgoe_net[3:] == '333': napgap[1] = 2
        elif lgoe_net[:3] == '333': napgap[1] = 1
        
    if lcode[0] in ['ea','ek','ei']:
        if lgoe_net[3:] == '232': napgap[1] = 1
        elif lgoe_net[:3] == '232': napgap[1] = 2
    if lcode[0] in ['eg','ee','ec']:
        if lgoe_net[3:] == '232': napgap[1] = 2
        elif lgoe_net[:3] == '232': napgap[1] = 1

    if lcode[0] in ['cc','ca','ck']:
        if lgoe_net[3:] == '223': napgap[1] = 1
        elif lgoe_net[:3] == '223': napgap[1] = 2
    if lcode[0] in ['ci','cg','ce']:
        if lgoe_net[3:] == '223': napgap[1] = 2
        elif lgoe_net[:3] == '223': napgap[1] = 1

    if lcode[0] in ['gk','gi','gg']:
        if lgoe_net[3:] == '322': napgap[1] = 1
        elif lgoe_net[:3] == '322': napgap[1] = 2
    if lcode[0] in ['ge','gc','ga']:
        if lgoe_net[3:] == '322': napgap[1] = 2
        elif lgoe_net[:3] == '322': napgap[1] = 1

    if lcode[0] in ['hd','hf','hh']:
        if lgoe_net[3:] == '233': napgap[1] = 1
        elif lgoe_net[:3] == '233': napgap[1] = 2
    if lcode[0] in ['hj','hl','hb']:
        if lgoe_net[3:] == '233': napgap[1] = 2
        elif lgoe_net[:3] == '233': napgap[1] = 1

    if lcode[0] in ['ff','fh','fj']:
        if lgoe_net[3:] == '323': napgap[1] = 1
        elif lgoe_net[:3] == '323': napgap[1] = 2
    if lcode[0] in ['fl','fb','fd']:
        if lgoe_net[3:] == '323': napgap[1] = 2
        elif lgoe_net[:3] == '323': napgap[1] = 1 

    if lcode[0] in ['jj','jl','jb']:
        if lgoe_net[3:] == '222': napgap[1] = 1
        elif lgoe_net[:3] == '222': napgap[1] = 2
    if lcode[0] in ['bd','bf','bh']:
        if lgoe_net[3:] == '222': napgap[1] = 2
        elif lgoe_net[:3] == '222': napgap[1] = 1

    if lcode[0] in ['dh','dj','dl']:
        if lgoe_net[3:] == '332': napgap[1] = 1
        elif lgoe_net[:3] == '332': napgap[1] = 2
    if lcode[0] in ['db','dd','df']:
        if lgoe_net[3:] == '332': napgap[1] = 2
        elif lgoe_net[:3] == '332': napgap[1] = 1
        
    #득시여부를 구한다.
    shi_1 = ['333323','323333','333222','323232','223332','233322','233223','223233']
    shi_2 = ['333322','222323','223322','233332','323332','232333']
    shi_3 = ['233232','332323','333332','332333','232233']
    shi_4 = ['333333','223223','233233','323323']
    shi_5 = ['233333','233323','232332','222322']
    shi_6 = ['233323','222332','223333','322232']
    shi_7 = ['332232','222232','332322','322233','332223','232222','332322','222333','232323']
    shi_8 = ['332233','222233','323222','322333','233222','223232','232223','333232','322223']
    shi_9 = ['323322','223222','322323','222223']
    shi_10 = ['232232','222222','332332']
    shi_11 = ['333233','323223','322222']
    shi_12 = ['333223','322322','232322','233323','332222']
    
    getshi = [False,False]
    
    if jeolki_index in [0,1]:
        if fgoe_net in shi_1: getshi[0] = True
        if lgoe_net in shi_1: getshi[1] = True
    elif jeolki_index in [2,3]:
        if fgoe_net in shi_2: getshi[0] = True
        if lgoe_net in shi_2: getshi[1] = True
    elif jeolki_index in [4,5]:
        if fgoe_net in shi_3: getshi[0] = True
        if lgoe_net in shi_3: getshi[1] = True
    elif jeolki_index in [6,7]:
        if fgoe_net in shi_4: getshi[0] = True
        if lgoe_net in shi_4: getshi[1] = True
    elif jeolki_index in [8,9]:
        if fgoe_net in shi_5: getshi[0] = True
        if lgoe_net in shi_5: getshi[1] = True
    elif jeolki_index in [10,11]:
        if fgoe_net in shi_6: getshi[0] = True
        if lgoe_net in shi_6: getshi[1] = True
    elif jeolki_index in [12,13]:
        if fgoe_net in shi_7: getshi[0] = True
        if lgoe_net in shi_7: getshi[1] = True
    elif jeolki_index in [14,15]:
        if fgoe_net in shi_8: getshi[0] = True
        if lgoe_net in shi_8: getshi[1] = True
    elif jeolki_index in [16,17]:
        if fgoe_net in shi_9: getshi[0] = True
        if lgoe_net in shi_9: getshi[1] = True        
    elif jeolki_index in [18,19]:
        if fgoe_net in shi_10: getshi[0] = True
        if lgoe_net in shi_10: getshi[1] = True
    elif jeolki_index in [20,21]:
        if fgoe_net in shi_11: getshi[0] = True
        if lgoe_net in shi_11: getshi[1] = True
    elif jeolki_index in [22,23]:
        if fgoe_net in shi_12: getshi[0] = True
        if lgoe_net in shi_12: getshi[1] = True

    return firstgoe,lastgoe,\
    cheonsu_sum,jisu_sum,wongi,banwongi,napgap,hwagong,banhwagong,getche,getshi
    

def get_harakisu_year(start_yearju,goe):
    """get_harakisu_year(start_yearju,goe) -> tuple
    Return harakisu year data
    - 'start_yearju' is a string like 'aa'.
    - 'goe' is a string like '333232'. It should be there is '6' or '9'.
    It'll be ignored.
    - Returned tuple is like ('923333','333623',...,'333239').
    The items number can be 6 or 9.
    - Programmed by herokims (2006. 10. 30.)
    - Translated from Visual Basic to Python in 2007. 6. 23.
    """
                      
    cnt = 0; pos = 0
    result = []
    
    try: intx = goe.index("6")
    except: intx = goe.index("9")
    
    intx += 1
    #만약 동효가 6이라면 시발년이 음년으로 파생해가는 유년괘는 6년간 변환하며, 본효부터 순차적으로 변한다
    if '6' in goe:
        
        for cnt in range(0,6):
            pos = intx + cnt
            
            #만약 상효를 넘을 경우, 6을 빼서 초효로 되돌아가도록 한다
            if pos > 6: pos -= 6

            #다음유년괘는 이전유년괘에서 바뀌어가는 것이므로 처음 입력받은 괘에 그대로 변화를 반영하여
            #루프를 돌린다
            goe = _reverse_hyo(goe,pos,True,True)
            result.append(goe)
    
    #만약 동효가 9이라면, 시발년도에 따라 달라지며,
    #세효-응효-세효순으로 변동된 이후 전체효가 반복되는 게 특징이다
    else:

        #첫번째 유년괘는 양년인지 여부에 따라 달라진다
        if isYanggan(start_yearju[0]):
            result.append(goe)
        elif not isYanggan(start_yearju[0]):
            goe = _reverse_hyo(goe,intx,True,True)
            result.append(goe)
        else:
            pass
        
        #두번째 유년괘는 응효가 변한 상태이다
        if intx == 1: goe = _reverse_hyo(goe,4,True,True); result.append(goe)
        elif intx == 2: goe = _reverse_hyo(goe,5,True,True); result.append(goe)
        elif intx == 3: goe = _reverse_hyo(goe,6,True,True); result.append(goe)
        elif intx == 4: goe = _reverse_hyo(goe,1,True,True); result.append(goe)
        elif intx == 5: goe = _reverse_hyo(goe,2,True,True); result.append(goe)
        elif intx == 6: goe = _reverse_hyo(goe,3,True,True); result.append(goe)
        else: 
            #나오지 않는것으로 검증되었음
            pass

        #세번째부터 아홉번째 유년괘는 동효가 6인경우와 비슷하다
        for cnt in range(2,9):
        
            pos = intx + cnt - 2
            
            #만약 상효를 넘을 경우, 6을 빼서 초효로 되돌아가도록 한다
            if pos > 6 : pos -= 6
            
            #다음유년괘는 이전유년괘에서 바뀌어가는 것이므로 처음 입력받은 괘에 그대로 변화를 반영하여
            #루프를 돌린다
            goe = _reverse_hyo(goe,pos,True,True)
            result.append(goe)
            
    result = tuple(result)
    
    return result


def get_harakisu_month(goe):
    """get_harakisu_month(goe) -> tuple
    Return harakisu month data
    - 'goe' is a string like '339232'. It should be there is '6' or '9'.
    It'll be ignored.
    - Returned tuple is like ('923333','333623',...,'333239').
    The items number will be 12.
    - Programmed by herokims (2006. 10. 30.)
    - Translated from Visual Basic to Python in 2007. 6. 23.
    """
    
    try: intx = goe.index("6")
    except: intx = goe.index("9")
    intx += 1
    
    result = list(" " * 12)
    even_month = ''
    
    for intx2 in range(0,6):
        
        #월괘는 유년괘 동효의 다음효부터 변하므로 1을 더한다
        pos = intx + intx2 + 1
        
        #만약 상효를 넘을 경우, 6을 빼서 초효로 되돌아가도록 한다
        if pos > 6 : pos -= 6
        
        #홀수월은 유년괘의 효를 하나씩 변화시켜 만든다
        goe = _reverse_hyo(goe,pos,True,True)
        result[intx2*2] = goe
        even_month = goe
        
        #짝수월은 홀수월 동효의 응효를 변화시켜 만든다
        if pos == 1: even_month = _reverse_hyo(even_month,4,True,True)
        elif pos == 2: even_month = _reverse_hyo(even_month,5,True,True)
        elif pos == 3: even_month = _reverse_hyo(even_month,6,True,True)
        elif pos == 4: even_month = _reverse_hyo(even_month,1,True,True)
        elif pos == 5: even_month = _reverse_hyo(even_month,2,True,True)
        elif pos == 6: even_month = _reverse_hyo(even_month,3,True,True)
        else:
            #나오지 않는것으로 검증되었음
            pass
        result[intx2*2 + 1] = even_month
    
    result = tuple(result)
    
    return result


def get_harakisu_day(goe):
    """get_harakisu_day(goe) -> tuple
    Return harakisu days data
    - 'goe' is a string like '339232'. It should be there is '6' or '9'.
    It'll be ignored.
    - Returned tuple is like ('923333','333623',...,'333239').
    The items number will be 30.
    - Programmed by herokims (2006. 10. 30.)
    - Translated from Visual Basic to Python in 2007. 6. 23.
    """
    
    try: intx = goe.index("6")
    except: intx = goe.index("9")
    intx += 1
    
    day5goe = ''
    ori_goe = goe
    result = list(" " * 30)
    
    #일괘를 계산할 때는 동효 자신을 제외한 나머지 5효를 하나씩 변화시키므로 0부터 4까지 루프를 돌린다
    for intx2 in range(0,5):
        
        #5일괘는 월괘 동효의 다음효부터 변하므로 1을 더한다
        pos = intx + intx2 + 1
        
        #만약 상효를 넘을 경우, 6을 빼서 초효로 되돌아가도록 한다
        if pos > 6: pos -= 6
        
        day5goe = _reverse_hyo(ori_goe,pos,True,True)
        for intx3 in range(0,6):
            day5goe = day5goe.replace('6','2')
            day5goe = day5goe.replace('9','3')
            
            day5goe = list(day5goe)            
            if day5goe[intx3] in ('2','6'): day5goe[intx3] = '6'
            elif day5goe[intx3] in ('3','9'): day5goe[intx3] = '9'
            else:
                #나오지 않는 것으로 검증되었음
                pass
            day5goe = "".join(day5goe)
                
            result[intx2 * 6 + intx3] = day5goe
    
    result = tuple(result)
    
    return result


def runTest():  
    
    print("현재 시각을 기준으로 한 하락이수(남성) :")
    otime = time.localtime()[:5]
    print(get_harakisu(otime,1))
    
    print("현재 시각을 기준으로 한 하락이수(여성) :")
    otime = time.localtime()[:5]
    print(get_harakisu(otime,2))
    
    print("사주예제(남성)의 하락이수 본괘:")
    otime = (1977,12,13,0,20)
    info = get_harakisu(otime,1)
    print(info[0] + " " + info[1])
    
    print("사주예제(남성)의 하락이수 대운별 괘흐름(선천):")
    startju = lifecode.get_current_lifecode()[0]
    first = get_harakisu_year(startju,info[0])
    print(first)

    print("사주예제(남성)의 하락이수 대운별 괘흐름(후천):")
    startju = lifecode.get_current_lifecode()[0]
    last = get_harakisu_year(startju,info[1])
    print(last)


if __name__ == '__main__':
    runTest()
    