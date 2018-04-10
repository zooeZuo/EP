#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'

from logging.handlers import RotatingFileHandler
import mock
import sys,os
import requests
import logging
import json
import random
from smartcard.util import toHexString
from apdu_scripts import scp02_channel as scp02
from apdu_scripts.command_apdu import CAPDU


exePath = os.path.split(sys.path[0])[0]
# sys.path[0].replace('\ResetCard.exe','') #Make sure the file dir is correct both in python script and  exe
# Log Setting
LOG_PATH_FILE = os.path.split(sys.path[0])[0] + "\\" + "ResetCard.log"
LOG_MODE = 'a'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10M
LOG_MAX_FILES = 5  # 4 Files: Cap2Cos.log.1, Cap2Cos.log.2, Cap2Cos.log.3, Cap2Cos.log.4
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s %(levelname)-10s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s"
handler = RotatingFileHandler(LOG_PATH_FILE, LOG_MODE, LOG_MAX_SIZE, LOG_MAX_FILES)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)


class SEClient(object):

    def receicve_request(self,request):

        url = 'http://192.168.39.110:8080/SHSRC/TSM/1/1/PostApduResults'

        if request.method == 'POST':

            req = json.loads(request.body)

            if req.has_key('apduModelList'):
                length = req['apduModelList']
                i = random.randint(0,length-1)
                apdu = req['apduModelList'][i]['apdu']
                logger.debug('<-APDU:'+ str(toHexString(apdu)).replace(' ',''))



