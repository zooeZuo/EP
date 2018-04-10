#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
import json
import logging
import requests
from apdu_scripts import response_data as RD
from apdu_scripts.command_apdu import CAPDU,SelectFile,GetApplicationVersion,\
    GetApplicationInformation,GetChallenge,InitializeForLoad,StoreData,CreditForLoad,\
    Extradition
from apdu_scripts.response_apdu import RAPDU

def check_apdu(apdu):
    if type(apdu[:4]) == CAPDU.COMMANDS.values():
        logging.debug('指令类型：%s' % CAPDU.COMMANDS.keys())
        logging.debug('<-apdu: %s' % apdu)
    else:
        logging.error('没有该指令类型')
        logging.error('<-apdu: %s' % apdu)

def apdu_response():
    if SelectFile:
        res = RD.SELECT_FILE + '9000'
        response = requests.Response(res)
        logging.debug('->apdu: %s' % response)

    elif GetApplicationVersion:
        pass

class NFC_OTA(object):
    def recv_data(self,request):
        if request.method == 'POST':
            req = json.loads(request.body)
            if req.has_key('apduModelList'):
                pass
