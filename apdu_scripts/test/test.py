#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'

import random
from apdu_scripts.command_apdu import CAPDU
from smartcard.util import toHexString

data = {"apduModelList":[{"apdu":"00A404000EA0000003B0414D53442053425400","expStatusRegEx":"9000"},{"apdu":"805020000861763E10DD444246","expStatusRegEx":"9000"}]}
res_select = '6F328409A00000000386980701A5259F0801029F0C1E869820007590FFFF82052000B2D0614C800960A720140504201605040914'
sw = '9000'
print('<-APDU: ' + data["apduModelList"][0]["apdu"])

length = len(data["apduModelList"])


for index in data["apduModelList"]:
    if index['apdu'].startswith('00A4'):
        print('Select File:')
        print('<-APDU: ' + index['apdu'])
        print('->APDU: ' + res_select + sw)
    elif index['apdu'].startswith('8050'):
        print('Initialize For Load:')
        print('<-APDU: ' + index['apdu'])

i = random.randint(0,length-1)
print('<-APDU: ' + data["apduModelList"][i]["apdu"])
apdu = data["apduModelList"][i]["apdu"]

b = apdu[:4]
print(b)
capdu = CAPDU()
values = capdu.COMMANDS.values()
a = str(toHexString(values)).replace(' ','')
if b == a:
   c = CAPDU.COMMANDS.items()
   print(c)
else:
    print('no')