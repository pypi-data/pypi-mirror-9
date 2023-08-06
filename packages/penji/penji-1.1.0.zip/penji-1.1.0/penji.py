# -*- coding: cp949 -*-
"""PENJi의 개인 모듈"""

from math import *
from datetime import *
import struct

"""모듈 전역 변수 시작"""
primeList = []
now1 = datetime.now()
now2 = datetime.now()
"""모듈 전역 변수 끝"""

def TimerStart():
    global now1
    now1 = datetime.now()

def TimerStop():
    global now1, now2
    now2 = datetime.now()
    print "수행 시간 : ",
    print now2 - now1

def binaryWrite(filename, list1):
    binfile = open(filename, 'wb')
    for prime in list1:
        data = struct.pack('Q', prime)
        binfile.write(data)
    binfile.close()

def binaryRead(filename, list1):
    try:
        binfile = open(filename, 'rb')
    except:
        print('파일이 없어 직접 소수 리스트를 생성합니다')
        return
    strsize = struct.calcsize('Q')
    list1 = []
    while 1:
        data = binfile.read(strsize)
        if data == '':
            break       
        num = list(struct.unpack('Q', data))[0]
        list1.append(num)



def PrintErrMsg(code):
    err_header = 'ERROR(' + str(code) + ') : '
    err_msg = {
        0:"자연수 인자를 넣어주세요.",
        1:"2 이상의 자연수 인자를 넣어주세요.",
        2:"FORMAT은 1 ~ 3의 정수값만 가질 수 있습니다",
        3:"DEBUG의 값은 True 또는 False만 가질 수 있습니다",
        4:"검증할 수 없는 인자입니다",
        5:"리스트 인자를 넣어주세요",
        6:"리스트의 모든 원소는 자연수여야만 합니다"
    }
    print(err_header + err_msg.get(code))

def VerifyParam(var, param_string):
    """
    이 함수는 API가 아닙니다. 독자적으로 호출하여 사용시 문제 발생의 여지가 있습니다.
    
    해당 인자의 유효성을 검증합니다.
    """
    if param_string == 'FORMAT':
        if not(isinstance(var, int) and var >= 1 and var <= 3):
            PrintErrMsg(2)
            return False
        else:
            return True
    elif param_string == 'DEBUG':
        if not(isinstance(var, bool)):
            PrintErrMsg(3)
            return False
        else:
            return True
    elif param_string == 'NUM_LIST':
        if not(isinstance(var, list)):
            PrintErrMsg(5)
            return False
        for each in var:
            if not(isinstance(each, int) and each > 0):
                PrintErrMsg(6)
                return False
        return True
    else:
        PrintErrMsg(4)
        return False



def MakePrimeList(length, FILESAVE=False, FILELOAD=False):
    """length만큼의 소수 리스트를 반환합니다"""
    if not(isinstance(length, int) and length > 0):
        PrintErrMsg(0)
        return
    if length == 1: return [2]
    TimerStart()
    global primeList
    if FILELOAD:
        binaryRead('pList', primeList)
    pList = [2]
    i = 3
    if len(primeList) > 0:
        pList = primeList
        i = pList[-1] + 2
    while len(pList) < length:
        sw = True
        sqrt = i ** 0.5
        for k in range(1, len(pList)):            
            if i % pList[k] == 0:
                """print(str(i) + " 은 소수가 아님")"""
                sw = False                
                break
            if pList[k] > sqrt:
                break                
        if sw:
            """print("소수 발견 : " + str(i))"""
            pList.append(i)
        i += 2
    if FILESAVE:
        binaryWrite('pList', primeList)
    primeList = pList
    TimerStop()
    return pList



def MakeRangedPrimeList(low, high):
    """low ~ high범위 사이의 소수 리스트를 반환합니다"""
    if not(isinstance(low, int) and isinstance(high, int)):
        PrintErrMsg(0)
        return
    if not(low >= 2 and high >= 2):
        PrintErrMsg(1)
        return
    if low > high:
        temp = low
        low = high
        high = temp

    global primeList
    pList = []
    target = low
    while target <= high:
        sw = True
        for each in range(2, target):
            if target % each == 0:
                sw = False
        if sw:
            pList.append(target)            
        target += 1
    primeList = pList
    return pList



def GetLastPrimeList():
    """
    이 함수는 API가 아닙니다. 독자적으로 호출하여 사용시 문제 발생의 여지가 있습니다.
    
    마지막으로 생성한 소수 리스트를 반환합니다
    """
    global primeList
    return primeList



def InitPrimeList(num, DEBUG=False):
    """
    이 함수는 API가 아닙니다. 독자적으로 호출하여 사용시 문제 발생의 여지가 있습니다.
    
    pList를 초기화합니다. 기존의 primeList를 재사용하거나 여의치 않는 경우
    새 소수 리스트를 만듭니다.
    """
    if not(VerifyParam(DEBUG, 'DEBUG')): return
    
    global primeList
    if len(primeList) > 0 and primeList[0] == 2 and primeList[-1] > num:
        if DEBUG:
            print("primeList 재사용")
        return primeList
    else:
        if DEBUG:
            print("새 소수 리스트를 생성")
        if num == 2:
            return MakeRangedPrimeList(2, 2)
        else:
            return MakeRangedPrimeList(2, num - 1)
    

def IsPrime(num, DEBUG=False):
    """num의 소수 여부를 반환합니다. DEBUG는 분석 결과를 보여줄지 결정합니다"""
    if not(isinstance(num, int) and num >= 2):
        PrintErrMsg(1)
        return
    if not(VerifyParam(DEBUG, 'DEBUG')): return

    pList = InitPrimeList(num, DEBUG)
    for prime in pList:
        if(num % prime == 0):
            if DEBUG:
                print("소수 아님 : " + str(num) + "은(는) " + str(prime) + "으로 분해됨")
            return False
    if DEBUG:
        print(str(num) + " 은(는) 소수")
    return True



def IntegerFactorization(num, FORMAT=1, DEBUG=False):
    """
    num을 소인수분해하여 리스트로 반환합니다.

    DEBUG는 분석 결과를 보여줄지 결정합니다
    FORMAT은 리스트의 차원을 설정합니다.
        ex) 360을 소인수분해하여 2*2*2*3*3*5의 결과를 얻은 경우
        1 : [2, 2, 2, 3, 3, 5]로 반환됩니다. 즉 2*2*2*3*3*5의 형태를 갖습니다.
        2 : [ [2,3], [3,2], [5,1] ]로 반환됩니다. 즉 2^3 * 3^2 * 5^1의 형태를 갖습니다.
        3 : [5, 8 ,9]로 반환됩니다. 즉 5*8*9의 형태를 같습니다.
    """
    if not(isinstance(num, int) and num >= 2):
        PrintErrMsg(1)
        return
    if not(VerifyParam(FORMAT, 'FORMAT')): return
    if not(VerifyParam(DEBUG, 'DEBUG')): return

    pList = InitPrimeList(num, DEBUG)
    factorList = []

    num2 = num
    while num2 > 1:
        for prime in pList:
            if num2 % prime == 0:
                if DEBUG:
                    print(str(num2) + "은(는) " + str(prime) + "으로 분해됨")
                if FORMAT == 1:
                    factorList.append(prime)
                elif FORMAT == 2:
                    sw = True
                    for each in factorList:
                        if each[0] == prime:
                            sw = False
                            each[1] += 1
                    if sw2:
                        factorList.append([prime, 1])
                elif FORMAT == 3:
                    sw = True
                    for i in range(len(factorList)):
                        if factorList[i] % prime == 0:
                            sw = False
                            factorList[i] *= prime 
                    if sw2:
                        factorList.append(prime)
                num2 /= prime
                break
        if len(factorList) == 0:
            if DEBUG:
                print(str(num) + " 은(는) 소수")
            if FORMAT == 1 or FORMAT == 3:
                factorList.append(num)
            elif FORMAT == 2:
                factorList.append([num, 1])
            break
    return factorList

def lcm(num_list, FORMAT=1, DEBUG=False):
    """
    자연수 리스트를 인자로 받아 최소공배수를 구하여 반환합니다
    """
    """
    DEBUG는 분석 결과를 보여줄지 결정합니다
    FORMAT은 리스트의 차원을 설정합니다.
        ex) [72, 192] 정수 리스트를 받아 최소공배수 576을 구한 경우
        1 : 576을 반환합니다.
        2 : [2, 2, 2, 2, 2, 2, 3, 3]로 반환됩니다. 즉 2*2*2*2*2*2*3*3의 형태를 갖습니다.
        3 : [ [2,6], [3,2] ]로 반환됩니다. 즉 2^6 * 3^2의 형태를 갖습니다.
    """
    if not(VerifyParam(num_list, 'NUM_LIST')): return
    if not(VerifyParam(FORMAT, 'FORMAT')): return
    if not(VerifyParam(DEBUG, 'DEBUG')): return

    num_list.sort()
    pList = InitPrimeList(num_list[-1], DEBUG)
    factorList = []

    for prime in pList:
        sw = True
        while sw:
            sw2 = False
            sw4 = True
            for index in range(len(num_list)):
                if num_list[index] % prime == 0:
                    if sw4:
                        sw4 = False
                        factorList.append(prime)
                        if DEBUG: print(factorList)
                    num_list[index] /= prime
                    sw2 = True
            sw = sw2
        sw3 = True
        for index in range(len(num_list)):
            if num_list[index] != 1:
                sw3 = False
                break
        if sw3 == True:
            break

    if FORMAT == 1:
        lcm_var = 1
        for factor in factorList:
            lcm_var *= factor
        return lcm_var
    elif FORMAT == 2:
        return factorList
    elif FORMAT == 3:
        factorList2 = list(set(factorList))
        factorList3 = []
        for factor in factorList2:
            temp = [factor,0]
            for each in factorList:
                if each == factor:
                    temp[1] += 1
            factorList3.append(temp)
        return factorList3

        
                    
            
