#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/12
# descriptions :Response APDU
# vision      :
# copyright   :All copyright reserved by FMSH company
from __future__ import division, absolute_import, print_function, unicode_literals
__author__ = 'zuodengbo'
from apdu_scripts.tlv_structures import TLV

class RAPDU(object):
    """Response Application Protocol Data Unit"""

    def __init__(self):
        self.data = None
        self.sw1 = None
        self.sw2 = None

    @staticmethod
    def unmarshal(data):
        assert len(data) > 1

        sw1 = data[-2]
        sw2 = data[-1]

        assert sw1 not in (0x61,0x9F) #应该由传输层来处理

        if sw1 == 0x90 and sw2 == 0x00:
            obj = SuccessResponse()
        elif sw1 in (0x62,0x63):
            obj = WarningResponse()
        else:
            obj = ErrorResponse()

        obj.sw1 = sw1
        obj.sw2 = sw2

        if len(data) > 2:
            obj.data = TLV.unmarshal(data[:-2]) #TLV格式
        else:
            obj.data = None

        if type(obj) == ErrorResponse:
            raise obj

        return obj

    # 状态码
    def get_status(self):
        return "SW1: %02x, SW2: %02x, SW: %04x" % (self.sw1,self.sw2,self.sw1+self.sw2)

    #返回数据+状态码
    def __repr__(self):
        res = "<%s:'%s'" % (self.__class__.__name__,self.get_status())
        if self.data:
            res += ',data: '+ str(self.data)

        return res + ">"

    def __str__(self):
        return repr(self)

class SuccessResponse(RAPDU):
    """For successful response"""
    def get_status(self):
        return "成功"

class WarningResponse(RAPDU):
    """For warning"""

    WARNING = {
            0x62:{
                0x00:"无信息提供",
                0x81:"回送的数据可能有错",
                0x82:"文件长度<Le",
                0x83:"选择的文件无效",
                0x84:"FCI 格式与P2 指定的不符",
                lambda Cx: Cx[0] =='C'and '%s' % Cx[1]:"验证失败，还剩下()次尝试机会",
            },
            0x63:{
                0x00:"认证失败",
                lambda Cx: Cx[0] == 'C' and '%s' % Cx[1]:"验证失败，还剩下()次尝试机会"
            }
        }
    def get_status(self):
        if (self.sw1, self.sw2) in self.WARNING:
            return self.WARNING.get((self.sw1, self.sw2))

class ErrorResponse(RAPDU):
    """For errors"""
    ERRORS = {        
        0x64:{0x00:"标志状态位未变"},
        0x65:{0x81:"内存失败"},
        0x66:{0x01:"接收通讯超时",
              0x02:"校验和不对",
              0x03:"当前DF 文件无FCI",
              0x04:"当前DF 下无SF 或KF"},
        0x67:{0x00:"长度错误"},
        0x68:{0x82:"不支持安全报文"},
        0x69:{0x00:"不能处理",
              0x01:"命令不接受（无效状态）",
              0x81:"命令与文件结构不相容",
              0x82:"不满足安全状态",
              0x83:"因卡片密钥被锁拒绝迁出",
              0x84:"未取随机数",
              0x85:"使用条件不满足",
              0x86:"使用条件不满足（未建立钱包文件，圈存金额小于已透支金额,交易计数器达到最大值）",
              0x87:"安全报文数据项丢失",
              0x88:"MAC验证失败"},
        0x6A:{0x80:"数据域参数错误（交易金额超出最大金额限制）",
              0x81:"功能不支持",
              0x82:"未找到文件",
              0x83:"未找到记录",
              0x84:"文件中存储空间不够",
              0x86:"参数P1 P2错误",
              0x87:"Lc与P1-P2不一致"},
        0x6B:{0x00:"参数错误（偏移地址超出了EF）"},
        0x6C:{0xFF:"长度错误（Le 错误；'FF'为实际长度）"},
        0x6D:{0x00:"不支持的指令代码"},
        0x6E:{0x00:"不支持的类：CLA 错"},
        0x6F:{0x00:"数据无效"},
        0x93:{0x01:"金额不足",
              0x02:"MAC 无效",
              0x03:"应用永久锁住"},
        0x94:{0x01:"金额不足",
              0x02:"交易计数器到达最大值",
              0x03:"密钥索引不支持",
              0x06:"所需MAC不可用"}

    }
    def get_status(self):
        if (self.sw1,self.sw2) in self.ERRORS:
            return self.ERRORS.get((self.sw1,self.sw2))
        else:
            return "Unkown error: %02x %02x" % (self.sw1,self.sw2)


if __name__=='__main__':
    s = RAPDU()
    #print(s.get_status())
    print(s.unmarshal('6F328409A00000000386980701A5259F0801029F0C1E869820007590FFFF82052000B2D0614C800960A7201405042016050409149000'))
