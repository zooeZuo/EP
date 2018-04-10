#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/11
# discription :command apdu
# vision      :
# copyright   :All copyright reserved by FMSH company
from __future__ import division,absolute_import,print_function,unicode_literals

__author__ = 'zuodengbo'
from util import format_bytes
import logging
import nonce
import six

def assert_vaild_byte(val):
    assert type(val) == int
    assert val < 0xFF
    assert val >= 0x00

class CAPDU(object):
    """Command APDU

        Defined in ISO-7816-4
    """
    #将命令的类名映射到CLA，INS字节
    COMMANDS = {
        #通用指令
        'SelectFile':[0x00, 0xA4],#选择文件
        'GetApplicationVersion':[0x80,0x0A],#获取应用版本信息
        'StoreData':[0x80 or 0x84,0xE2],#写入数据
        'Install': [0x80 or 0x84, 0xE6],  # 安装
        'Load':[0x80 or 0x84,0xE8],# 加载
        'ManageChannel':[0x00,0x70],# 管理通道
        'PutKey':[0x80 or 0x84,0xD8],# 密钥
        'SetStatus':[0x80 or 0x84,0xF0],# 设置状态
        'GetStatus':[0x80 or 0x84,0xF2],# 取得状态
        'GetData':[0x00 or 0x80 or 0x84,0xCA],# 取数据
        #个人化阶段指令
        'GetChallenge':[0x00,0x84],#取随机数
        'GetApplicationInformation':[0x00,0x0A],#获取应用版本信息
        'InitializeForLoad':[0x80,0x50],#圈存初始化
        'CreditForLoad':[0x80,0x52],#圈存命令
        'Extradition':[0x84,0xBE]#应用迁出指令
    }

    #file选择方式
    ADF = {
        'AID':'A00000000386980701',
        'FID':'3F01'
    }

    def __init__(self):
        self.name = None
        self.data = None
        self.p1 = None
        self.p2 = None
        self.lc = None
        self.le = None


    #命令排列
    def marshal(self):
        cla,ins = self.COMMANDS.get(self.__class__.__name__)

        for val in [cla,ins,self.p1,self.p2,]:
            assert_vaild_byte(val)

        #强制性命令头
        cmd = [cla,ins,self.p1,self.p2]

        #非强制部分
        if self.data is not None:

            cmd += [len(self.data)]
            cmd += self.data

        #期望字节长度
        if self.le is not None:
            cmd += [self.le] # Le
        return cmd


    def get_class(self, pdu_bytes):
        for cls_name,b in self.COMMANDS.items():
            if pdu_bytes == b:
                return globals()[cls_name]
        return None

    #命令数据编出
    def unmarshal(self, data):

        pcls = self.get_class(data[:2])
        obj = object.__new__(pcls)
        obj.p1 = data[2]
        obj.p2 = data[3]
        if len(data) > 5:
            obj.lc = data[4]
            obj.data = data[5:obj.lc + 5]
        if len(data) > obj.lc + 5:
            obj.le = data[-1]
        else:
            obj.le = None
        return obj

    def __repr__(self):
        return '<Command[%s] P1:%02x,P2:%02x, data: %s, Le: %02x>' % (
            self.name,self.p1,self.p2,format_bytes(self.data),self.le or 0)

class SelectFile(CAPDU):
    """Select ADF from the card by AID or FID"""

    name = 'SelectFile'

    def __init__(self,AID=None, FID=None,next_occurrence=False):
        super(SelectFile, self).__init__()


        if AID is not None:
            if isinstance(AID,six.string_types):# 使用AID选择
                self.data = [ord(c) for c in AID]

            else:
                self.data = AID
            self.p1 = 0x04
            assert 10 <= len(self.data) <= 32

        else:
            self.data = FID #使用FID选择
            self.p1 = 0x00
            assert len(self.data) == 4


        if next_occurrence:
            self.p2 = 0x00 #第一次或者只发生

        self.le = 0x00

class GetApplicationVersion(CAPDU):
    """ Get application version to obtain information about the application version of the traffic card

        INNER_VERSION = (0x00,0x01 or 0x80) #获取内部版本号
        OUTER_VERSION = (0x00,0x02) #获取外部版本号
    """

    name = 'GetApplicationVersion'


    def __init__(self,obj):
        super(GetApplicationVersion, self).__init__()
        assert type(obj) == tuple

        self.p1 = 0x00
        self.p2 = 0x01 or 0x80 or 0x02
        if self.p2 == 0x01 or 0x80:
            logging.debug(u'获取内部版本号')
        elif self.p2 == 0x02:
            logging.debug(u'获取外部版本号')
        self.data = None
        self.le = 0x00

class StoreData(CAPDU):
    """Store data used for writing personalization data to ADF"""

    name = 'StoreData'

    def __init__(self, obj,personal_data):
        super(StoreData, self).__init__()

        self.p1 = 0x00 or 0x80
        assert_vaild_byte(obj)
        if 0xFF > obj > 0x00:
            self.p2 = obj

        self.data = personal_data
        self.le = None

class ManageChannel(CAPDU):
    """manage channel"""
    name = 'ManageChannel'

    def __init__(self):
        super(ManageChannel, self).__init__()
        self.p1 = 0x00 or 0x80
        if self.p1 == 0x00:
            logging.debug('open logic channel')
        elif self.p1 == 0x80:
            logging.debug('close logic channel')
        self.p2 = 0x00 or 0x01 or 0x02 or 0x03
        self.data = None
        if self.p1 - self.p2 == 0x0000:
            self.le = 0x01
        else:
            self.le = None


class GetChallenge(CAPDU):
    """Get challenge use for line protection process"""

    name = 'GetChallenge'

    def __init__(self):
        super(GetChallenge, self).__init__()

        self.p1 = 0x00
        self.p2 = 0x00
        self.data = None
        if self.le == 0x04:
            logging.debug('取4字节随机数')
        elif self.le == 0x08:
            logging.debug('取8字节随机数')
        elif self.le == 0x10:
            logging.debug('取10字节随机数')

class GetApplicationInformation(CAPDU):
    """Used for getting the traffic card application version information,

     mainly include: internal version number, external version number,

     the application life cycle state, ordering information
     """

    name = 'GetApplicationInformation'

    SERIAL = nonce.Terminal_Generator_8() #8字节终端随机数

    def __init__(self,data):
        super(GetApplicationInformation, self).__init__()


        if self.p1 == 0x00 and self.p2 == 0x01 or 0x80:

            self.data = None
            self.le = 0x00
            logging.debug('获取内部版本号')
        elif self.p1 == 0x00 and self.p2 == 0x02:

            self.data = None
            self.le = 0x00
            logging.debug('获取外部版本号')
        elif self.p1 == 0x00 and self.p2 == 0x03:

            self.data = None
            self.le = 0x00
            logging.debug('获取应用生命周期状态')
        elif self.p1 == 0x01 or 0x02 or 0x07 or 0x5A and self.p2 == 04:
            if self.p1 == 0x01:
                logging.debug('根据主版本号')
            elif self.p1 == 0x02:
                logging.debug('根据次版本号')
            elif self.p1 == 0x07:
                logging.debug('根据修订版本号')
            elif self.p1 == 0x5A:
                logging.debug('根据发行模式')

            self.data = data #data = nonce.Terminal_Generator_8()
            self.le =None
            logging.debug('获取订购信息')

class InitializeForLoad(CAPDU):
    """Used in Shanghai bus card application to initialize the credit for load transaction.

        GMPK= 0x01 #圈存密钥索引号
        AMOUNTS = 0x00015F90 #交易金额
        TERMINAL_NUM = nonce.Terminal_Generator_6() #终端机编号
    """

    name = 'InitializeForLoad'



    def __init__(self,data):
        super(InitializeForLoad, self).__init__()


        self.p1 = 0x00
        self.p2 = 0x02 #用于电子钱包

        self.data = data #data = GMPK+AMOUNTS+TERMINAL_NUM
        self.le = 0x10


class CreditForLoad(CAPDU):
        """For the EP of Shanghai bus card application credit for load transaction.

            RADE_DATE = 20180115#datetime.date() #交易日期
            TRANSACTION_TIME = 155235#datetime.time() #交易时间
            MAC2 = 0xA158557B
        """

        name = 'CreditForLoad'

        def __init__(self,data):
            super(CreditForLoad, self).__init__()


            self.p1 = 0x00
            self.p2 = 0x00

            self.data = data #data = TRADE_DATE+TRANSACTION_TIME+MAC2
            self.lc = 0x04

class Extradition(CAPDU):
     """After the instruction is successful, the application enters the "migration" state

        EVACUATION_DATE = 20180125#datetime.date() # 迁出日期
        EFFECTIVE_DATE = 0x0A # 有效期
        SERIAL = 0x00002E09 # 4字节流水
        MAC = 0xD737B231 #应用迁移验证码
     """

     name = 'Extradition'


     def __init__(self,data):
         super(Extradition, self).__init__()


         self.p1 = 0x00
         self.p2 = 0x00

         self.data = data #data = EVACUATION_DATE+EFFECTIVE_DATE+SERIAL+MAC
         self.le = None