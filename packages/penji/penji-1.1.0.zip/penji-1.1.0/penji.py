# -*- coding: cp949 -*-
"""PENJi�� ���� ���"""

from math import *
from datetime import *
import struct

"""��� ���� ���� ����"""
primeList = []
now1 = datetime.now()
now2 = datetime.now()
"""��� ���� ���� ��"""

def TimerStart():
    global now1
    now1 = datetime.now()

def TimerStop():
    global now1, now2
    now2 = datetime.now()
    print "���� �ð� : ",
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
        print('������ ���� ���� �Ҽ� ����Ʈ�� �����մϴ�')
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
        0:"�ڿ��� ���ڸ� �־��ּ���.",
        1:"2 �̻��� �ڿ��� ���ڸ� �־��ּ���.",
        2:"FORMAT�� 1 ~ 3�� �������� ���� �� �ֽ��ϴ�",
        3:"DEBUG�� ���� True �Ǵ� False�� ���� �� �ֽ��ϴ�",
        4:"������ �� ���� �����Դϴ�",
        5:"����Ʈ ���ڸ� �־��ּ���",
        6:"����Ʈ�� ��� ���Ҵ� �ڿ������߸� �մϴ�"
    }
    print(err_header + err_msg.get(code))

def VerifyParam(var, param_string):
    """
    �� �Լ��� API�� �ƴմϴ�. ���������� ȣ���Ͽ� ���� ���� �߻��� ������ �ֽ��ϴ�.
    
    �ش� ������ ��ȿ���� �����մϴ�.
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
    """length��ŭ�� �Ҽ� ����Ʈ�� ��ȯ�մϴ�"""
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
                """print(str(i) + " �� �Ҽ��� �ƴ�")"""
                sw = False                
                break
            if pList[k] > sqrt:
                break                
        if sw:
            """print("�Ҽ� �߰� : " + str(i))"""
            pList.append(i)
        i += 2
    if FILESAVE:
        binaryWrite('pList', primeList)
    primeList = pList
    TimerStop()
    return pList



def MakeRangedPrimeList(low, high):
    """low ~ high���� ������ �Ҽ� ����Ʈ�� ��ȯ�մϴ�"""
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
    �� �Լ��� API�� �ƴմϴ�. ���������� ȣ���Ͽ� ���� ���� �߻��� ������ �ֽ��ϴ�.
    
    ���������� ������ �Ҽ� ����Ʈ�� ��ȯ�մϴ�
    """
    global primeList
    return primeList



def InitPrimeList(num, DEBUG=False):
    """
    �� �Լ��� API�� �ƴմϴ�. ���������� ȣ���Ͽ� ���� ���� �߻��� ������ �ֽ��ϴ�.
    
    pList�� �ʱ�ȭ�մϴ�. ������ primeList�� �����ϰų� ����ġ �ʴ� ���
    �� �Ҽ� ����Ʈ�� ����ϴ�.
    """
    if not(VerifyParam(DEBUG, 'DEBUG')): return
    
    global primeList
    if len(primeList) > 0 and primeList[0] == 2 and primeList[-1] > num:
        if DEBUG:
            print("primeList ����")
        return primeList
    else:
        if DEBUG:
            print("�� �Ҽ� ����Ʈ�� ����")
        if num == 2:
            return MakeRangedPrimeList(2, 2)
        else:
            return MakeRangedPrimeList(2, num - 1)
    

def IsPrime(num, DEBUG=False):
    """num�� �Ҽ� ���θ� ��ȯ�մϴ�. DEBUG�� �м� ����� �������� �����մϴ�"""
    if not(isinstance(num, int) and num >= 2):
        PrintErrMsg(1)
        return
    if not(VerifyParam(DEBUG, 'DEBUG')): return

    pList = InitPrimeList(num, DEBUG)
    for prime in pList:
        if(num % prime == 0):
            if DEBUG:
                print("�Ҽ� �ƴ� : " + str(num) + "��(��) " + str(prime) + "���� ���ص�")
            return False
    if DEBUG:
        print(str(num) + " ��(��) �Ҽ�")
    return True



def IntegerFactorization(num, FORMAT=1, DEBUG=False):
    """
    num�� ���μ������Ͽ� ����Ʈ�� ��ȯ�մϴ�.

    DEBUG�� �м� ����� �������� �����մϴ�
    FORMAT�� ����Ʈ�� ������ �����մϴ�.
        ex) 360�� ���μ������Ͽ� 2*2*2*3*3*5�� ����� ���� ���
        1 : [2, 2, 2, 3, 3, 5]�� ��ȯ�˴ϴ�. �� 2*2*2*3*3*5�� ���¸� �����ϴ�.
        2 : [ [2,3], [3,2], [5,1] ]�� ��ȯ�˴ϴ�. �� 2^3 * 3^2 * 5^1�� ���¸� �����ϴ�.
        3 : [5, 8 ,9]�� ��ȯ�˴ϴ�. �� 5*8*9�� ���¸� �����ϴ�.
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
                    print(str(num2) + "��(��) " + str(prime) + "���� ���ص�")
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
                print(str(num) + " ��(��) �Ҽ�")
            if FORMAT == 1 or FORMAT == 3:
                factorList.append(num)
            elif FORMAT == 2:
                factorList.append([num, 1])
            break
    return factorList

def lcm(num_list, FORMAT=1, DEBUG=False):
    """
    �ڿ��� ����Ʈ�� ���ڷ� �޾� �ּҰ������ ���Ͽ� ��ȯ�մϴ�
    """
    """
    DEBUG�� �м� ����� �������� �����մϴ�
    FORMAT�� ����Ʈ�� ������ �����մϴ�.
        ex) [72, 192] ���� ����Ʈ�� �޾� �ּҰ���� 576�� ���� ���
        1 : 576�� ��ȯ�մϴ�.
        2 : [2, 2, 2, 2, 2, 2, 3, 3]�� ��ȯ�˴ϴ�. �� 2*2*2*2*2*2*3*3�� ���¸� �����ϴ�.
        3 : [ [2,6], [3,2] ]�� ��ȯ�˴ϴ�. �� 2^6 * 3^2�� ���¸� �����ϴ�.
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

        
                    
            
