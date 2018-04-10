#!/usr/bin/env python
# -*- coding:utf-8 -*-
# date        :2018/1/12
# descriptions :Data elements
# vision      :
# copyright   :All copyright reserved by FMSH company
from __future__ import division, absolute_import, print_function, unicode_literals

__author__ = 'zuodengbo'
from enum import Enum


class Parse(Enum):
    BYTES = 1
    ASCII = 2
    DOL = 3  # Data Object List
    DEC = 4  # Decimal encoded in hex
    DATE = 5  # Date encoded in hex digits as [0xYY 0xMM 0xDD]
    INT = 6  # Decode bytes as an integer
    COUNTRY = 7  # Decode bytes as an contractor code
    CURRENCY = 8
    TAG_LIST = 9  # A list of tag names
    HEX = 10


""" Tag, Description, Parsing, Shortname """
ELEMENT_TABLE = [
    (0x01, '预置金', Parse.DEC, None),
    (0x02, '充值金额', Parse.DEC, None),
    (0x03, '充值优惠金额', Parse.DEC, None),
    (0x04, '福利总额', Parse.DEC, None),
    (0x05, '发放日期', Parse.DATE, None),
    (0x06, '福利编号', Parse.ASCII, None),
    (0x07, '校验码', Parse.HEX, None),
    (0x08, '开卡优惠金额', Parse.DEC, None),
    (0x09, '应用方平台流水', Parse.ASCII, None),
    (0x0A, '厂商编码', Parse.ASCII, None),
    (0x0B, '预置金资金账户', Parse.DEC, None),
    (0x0C, '充值金资金账户', Parse.DEC, None),
    (0x0D, '优惠金资金账户', Parse.DEC, None),
    (0x0E, '福利账户', Parse.DEC, None),
    (0x12, '业务类型', Parse.ASCII, None),
    (0x14, '票卡类型', Parse.DEC, None),
    (0x15, '卡应用号)', Parse.HEX, None),
    (0x16, 'SEID', Parse.HEX, 'SEID'),
    (0x17, '实例AID', Parse.HEX, 'IAID'),
    (0x19, 'SEID(old)', Parse.HEX, None),
    (0x1A, '订单号', Parse.HEX, None),
    (0x1B, '终端类型', Parse.ASCII, None),
    (0x1C, '操作时间', Parse.DATE, None),
    (0x1D, '订单操作', Parse.DEC, None),
    (0x1E, '用户账号', Parse.ASCII, None),
    (0x1F, '订单类型', Parse.DEC, None),
    (0x20, '终端类型(old)', Parse.ASCII, None),
    (0x21, '地域', Parse.DEC, None),
    (0x22, '用户账号（new）', Parse.ASCII, None),
    (0x23, '用户密码(new)', Parse.ASCII, None),
    (0x28, '用户编号', Parse.DEC, None),
    (0x29, '资金渠道', Parse.DEC, None),
    (0x2A, '订单来源', Parse.DEC, None),
    (0x2B, '卡形态', Parse.DEC, None),
    (0x2C, '结算日期', Parse.DATE, None),
    (0x2D, '发票领取标志', Parse.DEC, None),
    (0x2E, '是否发送短信通知', Parse.DEC, None),
    (0x2F, '发送短信渠道', Parse.DEC, None),
    (0x30, '操作序号', Parse.ASCII, None),
    (0x31, '起止日期', Parse.DATE, None),
    (0x32, '厂商结算日期', Parse.DATE, None),
    (0x33, '业务产品标识', Parse.DEC, 'BPID'),
    (0x34, '押金标识', Parse.DEC, None),
    (0x35, '面额标识', Parse.DEC, None),
    (0x36, '计价策略标识', Parse.DEC, None),
    (0x37, '租期', Parse.DEC, None),
    (0x38, '租赁业务标识', Parse.DEC, None),
    (0x39, '预结算数据签名', Parse.HEX, None),
    (0x3A, '附加数据', Parse.HEX, None),
    (0x3B, '卡的控制状态', Parse.DEC, None),
    (0x3C, '续期时间', Parse.DATE, None),
    (0x3D, '钱包限额', Parse.DEC, None),
    (0x3E, '功能位图', Parse.DEC, None),
    (0x3F, '退卡数据', Parse.HEX, None),
    (0x40, '卡内数据的token', Parse.HEX, None),
    (0x41, '退卡差额', Parse.DEC, None),
    (0x42, '卡的押金', Parse.DEC, None),
    (0x43, '卡的余额', Parse.DEC, None),
    (0x44, '发卡数据类型', Parse.DEC, None),
    (0x45, '功能有效期', Parse.DEC, None),
    (0x46, '任务编号', Parse.ASCII, None),
    (0x47, '关联任务号', Parse.ASCII, None),
    (0x48, '卡信息', Parse.HEX, None),
    (0x49, '扩展短文件标识', Parse.ASCII, None),
    (0x4A, '卡内数据', Parse.HEX, None),
    (0x4B, '平台端证书', Parse.HEX, None),
    (0x4C, '平台端随机数', Parse.HEX, None),
    (0x4D, '签名结果', Parse.HEX, None),
    (0x4E, '产品编码', Parse.ASCII, None),
    (0x4F, '远程交易类型', Parse.DEC, None),
    (0x50, '远程控制类型', Parse.DEC, None),
    (0x51, '支付结果', Parse.HEX, None),
    (0x52, '厂商发票金额', Parse.DEC, None),
    (0x53, '租赁清算信息', Parse.HEX, None),
    (0x55, '安全域Aid', Parse.HEX, 'SDAID'),
    (0x56, 'dpanCode', Parse.HEX, None),
    (0x57, 'ScriptsInstanceId', Parse.HEX, None),
    (0x58, '租赁开始时间', Parse.DATE, None),
    (0x59, '金额', Parse.DEC, None),
    (0x5A, '业务操作结果', Parse.DEC, None),
    (0x62, '应用迁移认证序号', Parse.HEX, None),
    (0x63, '其他', Parse.HEX, None),
    (0x6F, 'FCI模板', Parse.BYTES, 'FCI'),
    (0x84, '专用文件', Parse.BYTES, 'DF'),
    (0x88, '短文件标识符', Parse.HEX, 'SFI'),
    (0x89, '认证码', Parse.HEX, None),

]

"""
 A list of tags which contain sensitive data, for redacting data for public display.
 This should be considered non-exhaustive and used with caution.
 Some cards may provide sensitive data with under issuer-specific tags.
"""
SENSITIVE_TAGS = {

}
