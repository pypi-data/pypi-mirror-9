# *-* coding: UTF8 -*-
#==============================================================================
"""
[keymoon.py] - Mempire Keymoon module

이 모듈은 기문둔갑 포국 기능을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__ver__ = '150114'
__since__ = '2006-10-01'
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


from mempy import ichingbase
from mempy import lifecode


class TimeTypeError(Exception):pass


def get_keymoon(otime):
    """get_keymoon(otime) -> tuple
    Return keymoon display data
    - 'otime' is a tuple like (2007,6,4,11,59). it should be solar date.
    - Returned tuple is like
            ('+6ek',
             ('ic@a#e$e?g','gh@b#f$f?n','dj@c#g$g?n',
             'ed@h#d$d?n','nb@i#n$n?n','cf@d#h$h?n',
             'fg@g#c$c?n','ji@f#b$b?n','he@e#a$a?n'),
             ('h','e','e'))
    It starts with 4th Gung and ends with 6th Gung. First string is Gukname. \
    Second tuple has Keymoon display info(9 items). On each item, \
    First 2 string means Cheoban and Jiban. And Next '@' Guseong. '#' Palmun, \
    '$' Palsin and '?' means Gongmang. Third tuple consists of Sunsu, Jikbu, Jiksa.
    - programmed by herokims (2007.6.11 17:50 ~ 6.12 00:36)
    """
    lcode = lifecode.get_lifecode(otime)
    jeolki_index = ichingbase.get_jeolki_index(otime)
    
    sangwon = ("aa","bb","cc","dd","ee","fd","ge","hf","ig","jh",
               "ag","bh","ci","dj","ek","fj","gk","hl","ia","jb")
    jungwon = ("ff","gg","hh","ii","jj","ai","bj","ck","dl","ea",
               "fl","ga","hb","ic","jd","ac","bd","ce","df","eg")
    hawon =   ("ak","bl","ca","db","ec","fb","gc","hd","ie","jf",
               "ae","bf","cg","dh","ei","fh","gi","hj","ik","jl")
    
    if lcode[2] in sangwon: won = 0
    elif lcode[2] in jungwon: won = 1
    elif lcode[2] in hawon: won = 2
    
    if 21<= jeolki_index <= 23 or 0<= jeolki_index <= 8:isyangdun = True
    else:isyangdun = False
    
    jeolki_info =(
    "852","963","174","396","417","528","417","528","639","936","825","714",
    "258","147","936","714","693","582","693","582","471","174","285","396")#ipchun starts
    
    guknum = jeolki_info[jeolki_index][won]
    
    if isyangdun: gukname = "+" + str(guknum) + lcode[3]
    else: gukname = "-" + str(guknum) + lcode[3]
    
    next_star_dic = {'a':'b','b':'c','c':'d','d':'e','e':'f','f':'g','g':'h','h':'a'}
    next_gate_dic = {'a':'b','b':'c','c':'d','d':'e','e':'f','f':'g','g':'h','h':'a'}
    next_angel_dic= {'a':'b','b':'c','c':'d','d':'e','e':'f','f':'g','g':'h','h':'a'}    
    right_g_dic = {'1':'6','6':'7','7':'2','2':'9','9':'4','4':'3','3':'8','8':'1'}
    left_g_dic =  {'6':'1','1':'8','8':'3','3':'4','4':'9','9':'2','2':'7','7':'6'}
    forward_g_dic = {'1':'2','2':'3','3':'4','4':'5','5':'6','6':'7','7':'8','8':'9','9':'1'}
    backward_g_dic ={'1':'9','9':'8','8':'7','7':'6','6':'5','5':'4','4':'3','3':'2','2':'1'}

    cheongan = ('e','f','g','h','i','j','d','c','b')
    
    if   lcode[3] in ('aa','bb','cc','dd','ee','ff','gg','hh','ii','jj'):sunsu,gongmang = 'e','kl'
    elif lcode[3] in ('ak','bl','ca','db','ec','fd','ge','hf','ig','jh'):sunsu,gongmang = 'f','ij'
    elif lcode[3] in ('ai','bj','ck','dl','ea','fb','gc','hd','ie','jf'):sunsu,gongmang = 'g','gh'
    elif lcode[3] in ('ag','bh','ci','dj','ek','fl','ga','hb','ic','jd'):sunsu,gongmang = 'h','ef'
    elif lcode[3] in ('ae','bf','cg','dh','ei','fj','gk','hl','ia','jb'):sunsu,gongmang = 'i','cd'
    elif lcode[3] in ('ac','bd','ce','df','eg','fh','gi','hj','ik','jl'):sunsu,gongmang = 'j','ab'
    
    if   gongmang == 'kl':dicgong ={'1':'n','2':'n','3':'n','4':'n','5':'n','6':'g','7':'n','8':'n','9':'n'}
    elif gongmang == 'ij':dicgong ={'1':'n','2':'g','3':'n','4':'n','5':'n','6':'n','7':'g','8':'n','9':'n'}
    elif gongmang == 'gh':dicgong ={'1':'n','2':'g','3':'n','4':'n','5':'n','6':'n','7':'n','8':'n','9':'g'}
    elif gongmang == 'ef':dicgong ={'1':'n','2':'n','3':'n','4':'g','5':'n','6':'n','7':'n','8':'n','9':'n'}
    elif gongmang == 'cd':dicgong ={'1':'n','2':'n','3':'g','4':'n','5':'n','6':'n','7':'n','8':'g','9':'n'}
    elif gongmang == 'ab':dicgong ={'1':'g','2':'n','3':'n','4':'n','5':'n','6':'n','7':'n','8':'g','9':'n'}
    
    #Display Cheonban
    pos_gan_dic = {}
    gan_pos_dic = {}
    if isyangdun:
        tmp = guknum
        for intx in range(0,9):
            pos_gan_dic[str(tmp)] = cheongan[intx]
            gan_pos_dic[cheongan[intx]] = str(tmp)
            if cheongan[intx] == sunsu: sunsugung = int(tmp)
            if int(tmp) >= 9: tmp = 1
            else:
                tmp =int(tmp)
                tmp +=1
    else:
        tmp = guknum
        intx2 = 0
        for intx in range(8,-1,-1):
            pos_gan_dic[str(tmp)] = cheongan[intx2]
            gan_pos_dic[cheongan[intx2]] = str(tmp)
            if cheongan[intx2] == sunsu: sunsugung = int(tmp)
            if int(tmp) <= 1: tmp = 9
            else:
                tmp = int(tmp)
                tmp -=1
            intx2 +=1
    
    dicland = pos_gan_dic
    tmp = ''
    
    #Recognize displayed Cheonban
    right_gan_dic = {}
    left_gan_dic = {}
    
    right_gan_dic[pos_gan_dic['1']] = pos_gan_dic['6']
    right_gan_dic[pos_gan_dic['6']] = pos_gan_dic['7']
    right_gan_dic[pos_gan_dic['7']] = pos_gan_dic['2']
    right_gan_dic[pos_gan_dic['2']] = pos_gan_dic['9']
    right_gan_dic[pos_gan_dic['9']] = pos_gan_dic['4']
    right_gan_dic[pos_gan_dic['4']] = pos_gan_dic['3']
    right_gan_dic[pos_gan_dic['3']] = pos_gan_dic['8']
    right_gan_dic[pos_gan_dic['8']] = pos_gan_dic['1']
    
    left_gan_dic[pos_gan_dic['1']] = pos_gan_dic['8']
    left_gan_dic[pos_gan_dic['8']] = pos_gan_dic['3']
    left_gan_dic[pos_gan_dic['3']] = pos_gan_dic['4']
    left_gan_dic[pos_gan_dic['4']] = pos_gan_dic['9']
    left_gan_dic[pos_gan_dic['9']] = pos_gan_dic['2']
    left_gan_dic[pos_gan_dic['2']] = pos_gan_dic['7']
    left_gan_dic[pos_gan_dic['7']] = pos_gan_dic['6']
    left_gan_dic[pos_gan_dic['6']] = pos_gan_dic['1']
    
    #Get Jikbu, Jiksa
    if   sunsugung==1: jikbu,jiksa = 'a','a'
    elif sunsugung==2: jikbu,jiksa = 'f','f'
    elif sunsugung==3: jikbu,jiksa = 'c','c'
    elif sunsugung==4: jikbu,jiksa = 'd','d'
    elif sunsugung==5: jikbu,jiksa = 'f','f'    #if Junggung, assume that jikbu, jiksa belong to Gongung
    elif sunsugung==6: jikbu,jiksa = 'h','h'
    elif sunsugung==7: jikbu,jiksa = 'g','g'
    elif sunsugung==8: jikbu,jiksa = 'b','b'
    elif sunsugung==9: jikbu,jiksa = 'e','e'
    
    time_gan = lcode[3][0]
    if time_gan == 'a': sunsuwhere = gan_pos_dic[sunsu]
    else: sunsuwhere = gan_pos_dic[time_gan]
    
    if sunsuwhere == '5': sunsuwhere = '2' #if Jikbu, Jiksa's position are decided to Junggung,
                                           #assume that they belong to Gongung
    
    #Make Cheonban Position Dictionary
    dicsky = {}
    dicsky[sunsuwhere] = sunsu
    tmp = right_g_dic[sunsuwhere]
    if pos_gan_dic['5']==sunsu: tmp2 = right_gan_dic[pos_gan_dic['2']]
    else: tmp2 = right_gan_dic[sunsu]
    
    for intx in range(1,8):
        dicsky[tmp] = tmp2
        tmp = right_g_dic[tmp]
        tmp2 = right_gan_dic[tmp2]
    dicsky['5'] = 'n'
    tmp = ''
    tmp2 = ''
    
    #Make Palsin Position Dictionary
    dicangel = {}
    dicangel[sunsuwhere] = 'a'
    if isyangdun:
        tmp = left_g_dic[sunsuwhere]
        tmp2 = next_angel_dic['a']
        for intx in range(1,8):
            dicangel[tmp] = tmp2
            tmp = left_g_dic[tmp]
            tmp2 = next_angel_dic[tmp2]
    else:
        tmp = right_g_dic[sunsuwhere]
        tmp2 = next_angel_dic['a']
        for intx in range(1,8):
            dicangel[tmp] = tmp2
            tmp = right_g_dic[tmp]
            tmp2 = next_angel_dic[tmp2]
    dicangel['5'] = 'n' #There isn't palsin in Junggung
    tmp = ''
    tmp2 = ''
    
    #Make Guseong Position Dictionary
    dicstar = {}
    dicstar[sunsuwhere] = jikbu
    tmp = left_g_dic[sunsuwhere]
    tmp2 = next_star_dic[jikbu]
    for intx in range(1,8):
        dicstar[tmp] = tmp2
        tmp = left_g_dic[tmp]
        tmp2 = next_star_dic[tmp2]
    dicstar['5'] = 'i'
    tmp = ''
    tmp2 = ''
    
    #Make Palmun Position Dictionary
    dicgate = {}
    time_gan_steps_table = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7,'i':8,'j':9}
    steps = time_gan_steps_table[time_gan]
    
    tmp = str(sunsugung)
    if time_gan != 'a':
        if isyangdun:
            for intx in range(1,steps+1):
                tmp = forward_g_dic[tmp]
        else:
            for intx in range(1,steps+1):
                tmp = backward_g_dic[tmp]
    
    if tmp == '5': tmp = '2'
    
    dicgate[tmp] = jiksa
    tmp = left_g_dic[tmp]
    tmp2 = next_gate_dic[jiksa]
    for intx in range(1,8):
        dicgate[tmp] = tmp2
        tmp = left_g_dic[tmp]
        tmp2 = next_gate_dic[tmp2]
    dicgate['5'] = 'n'
    
    #Display Matrix format
    data1 = (
        dicsky['4']+dicland['4']+'@'+dicstar['4']+'#'+dicgate['4']+'$'+dicangel['4']+'?'+dicgong['4'],
        dicsky['9']+dicland['9']+'@'+dicstar['9']+'#'+dicgate['9']+'$'+dicangel['9']+'?'+dicgong['9'],  
        dicsky['2']+dicland['2']+'@'+dicstar['2']+'#'+dicgate['2']+'$'+dicangel['2']+'?'+dicgong['2'],
        dicsky['3']+dicland['3']+'@'+dicstar['3']+'#'+dicgate['3']+'$'+dicangel['3']+'?'+dicgong['3'],
        dicsky['5']+dicland['5']+'@'+dicstar['5']+'#'+dicgate['5']+'$'+dicangel['5']+'?'+dicgong['5'],
        dicsky['7']+dicland['7']+'@'+dicstar['7']+'#'+dicgate['7']+'$'+dicangel['7']+'?'+dicgong['7'],
        dicsky['8']+dicland['8']+'@'+dicstar['8']+'#'+dicgate['8']+'$'+dicangel['8']+'?'+dicgong['8'],
        dicsky['1']+dicland['1']+'@'+dicstar['1']+'#'+dicgate['1']+'$'+dicangel['1']+'?'+dicgong['1'],
        dicsky['6']+dicland['6']+'@'+dicstar['6']+'#'+dicgate['6']+'$'+dicangel['6']+'?'+dicgong['6']
        )
    data2 = (sunsu,jikbu,jiksa)
    result = (gukname,data1,data2)
    
    return result


def runTest():
    
    otime = time.localtime()[:5]
    
    print("지금 이 순간의 기문포국을 보여줍니다.")
    print(str(get_keymoon(otime)))


if __name__ == '__main__':
    runTest()
