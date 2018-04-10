#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discription :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
import random

base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'),ord('A')+6)]
#二进制to十进制
def bin2dec(str_num):
    return str(int(str_num,2))

#十六进制to十进制
def hex2dec(str_num):
    return str(int(str_num.upper(),16))

#十进制to二进制
def dec2bin(str_num):
    num = int(str_num)
    mid = []
    while True:
        if num == 0:
            break
        num,rem = divmod(num,2)
        mid.append(base[rem])

    return ''.join([str(y) for y in min[:: -1]])

#十进制to八进制 oct()
#十进制to十六进制 hex()
def dec2hex(str_num):
    num = int(str_num)
    if num == 0:
        return '0'
    mid = []
    while True:
        if num == 0:
            break
        num, rem = divmod(num, 16)
        mid.append(base[rem])

    return ''.join([str(y) for y in min[:: -1]])

#十六进制to二进制
def hex2bin(str_num):
    return dec2bin(hex2dec(str_num.upper()))

#二进制to十六进制
def bin2hex(str_num):
    return dec2hex(bin2dec(str_num))

#十六进制to字符串
def hex2str(data, l=16):
    data = data[2:]
    if data[len(data) - 1] == 'L':
        data = data[:len(data) - 1]
    while len(data) < l:
        data = '0' + data
    return data.upper()


def rand_hex(length):
    num = ''
    for i in range(0, length):
        num += hex2str(hex(random.randint(0, 15)), 1)
    return num.upper()

#产生32随机数
def Task_Id_Generator():
    taskid = rand_hex(32)
    return taskid

#产生8字节终端随机数
def Terminal_Generator_8():
    terminal = rand_hex(8)
    return terminal

#产生6字节终端随机数
def Terminal_Generator_6():
    term = rand_hex(6)
    return term

#产生4字节流水
def Serial_4():
    serial = rand_hex(4)
    return serial

if __name__=='__main__':
    p=Terminal_Generator_8()
    q=Terminal_Generator_6()
    d = Serial_4()
    print p
    print q
    print d