#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/12
# discription :Data field
# vision      :
# copyright   :All copyright reserved by FMSH company
from __future__ import division, absolute_import, print_function, unicode_literals
__author__ = 'zuodengbo'
from . import command_apdu, response_apdu
import nonce
import requests
import logging


SELECT_FILE = 0x6F328409A00000000386980701A5259F0801029F0C1E869820007590FFFF82052000B2D0614C800960A720140504201605040914
GET_APPLICATION_VERSION = ''
STORE_DATA = None
GET_CHALLENGE = nonce.Terminal_Generator_8()
GET_APPLICATION_INFORMATION = ''
INITIALIZE_FOR_LOAD = 0x00030F980004010020A124BA1D7E073D
CREDIT_FOR_LOAD = 0x17B8946D
EXTRADITION = 0x1612120A00002E090102075A90800960A7F716C6B4905AD5C4D50F2C82170FFC5B7713B2C7D23E9AB1A3F06DD3AC7654112D93EBA7DE4B54AF309BF3F6E72E758AAD122E8EDC78DCC9A09FECB689F77350559A4D1DBBFC98CE

#selectfile命令响应
def SelectFileResponse():
    if command_apdu.SelectFile:
        r_data = SELECT_FILE
        res = r_data + response_apdu.SuccessResponse
        request = requests.Response(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse

#获取应用版本命令响应
def GetApplicationVersion():
    if command_apdu.GetApplicationVersion:
        r_data = GET_APPLICATION_VERSION
        res = r_data + response_apdu.SuccessResponse
        request = requests.Response(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse

#storedata命令响应
def StoreData():
    if command_apdu.StoreData:
        res = response_apdu.SuccessResponse
        request = requests.Response(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse

#取随机数命令响应
def GetChallenge():
    if command_apdu.GetChallenge:
        r_data = GET_CHALLENGE
        res = r_data + response_apdu.SuccessResponse
        request = requests.Response(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse

#获取应用信息命令响应
def GetApplicationInformation():
    if command_apdu.GetApplicationInformation:
        r_data = GET_APPLICATION_INFORMATION
        res = r_data + response_apdu.SuccessResponse
        request = requests.Response(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse

#圈存初始化命令响应
def InitializeForLoad():
    if command_apdu.InitializeForLoad:
        r_data = INITIALIZE_FOR_LOAD
        res = r_data + response_apdu.SuccessResponse
        request = requests.post(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse

#圈存命令响应
def CreditForLoad():
    if command_apdu.CreditForLoad:
        r_data = CREDIT_FOR_LOAD
        res = r_data + response_apdu.SuccessResponse
        request = requests.Response(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse

#迁出命令响应
def Extradition():
    if command_apdu.Extradition:
        r_data = EXTRADITION
        res = r_data + response_apdu.SuccessResponse
        request = requests.Response(res)
        logging.debug('<<<'.format(res))
        return request
    else:
        return response_apdu.ErrorResponse or response_apdu.WarningResponse