# -*- coding: cp949 -*-
"""PENJi의 개인 모듈"""

def MakePrimeList(length):
    """length만큼의 소수 리스트를 반환합니다"""
    if not(isinstance(length, int)):
        print("ERROR: 정수 인자를 넣어주세요. 빈 리스트가 반환됩니다")
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
