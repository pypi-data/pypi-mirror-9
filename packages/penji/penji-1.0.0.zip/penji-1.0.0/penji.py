# -*- coding: cp949 -*-
"""PENJi�� ���� ���"""

def MakePrimeList(length):
    """length��ŭ�� �Ҽ� ����Ʈ�� ��ȯ�մϴ�"""
    if not(isinstance(length, int)):
        print("ERROR: ���� ���ڸ� �־��ּ���. �� ����Ʈ�� ��ȯ�˴ϴ�")
        return []
    pList = []
    target = 2
    while len(pList) < length:
        sw = True
        for each in range(2, target):
            if target % each == 0:
                sw = False
        if sw:
            pList.append(target)            
        target += 1
    return pList
