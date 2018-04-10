#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as pk
from Crypto.Hash import SHA
from binascii import b2a_hex,a2b_hex

class Sign(object):
    pub_key = RSA.importKey(open('auth_2048_public.pem','r').read())
    pri_key = RSA.importKey(open('auth_2048_private.pem','r').read())

    """
        RSA签名
        data待签名数据
        最后的签名用base64编码
        return sig签名
    """
    @classmethod
    def sign(cls,data):
        has = SHA.new(a2b_hex(data))
        signer = pk.new(cls.pri_key)
        sig = signer.sign(has)
        return b2a_hex(sig)

    """
        RSA验签
        data待签名数据
        sig需要验签的签名
        return 验签是否通过bool值
    """
    @classmethod
    def verify(cls,data,sig):
        sig = a2b_hex(sig)
        has = SHA.new(a2b_hex(data))
        ver = pk.new(cls.pub_key)
        return ver.verify(has,sig)


def main():
    obj = Sign()
    raw_data = '03000001007001292000552305010203040927044D492035850CA000000003464D534854534D2409A0000000038698070191040100057A510E5352435F534354435F303030303155011089030020001101810905000000000199051605251375'
    sign_data = obj.sign(raw_data)
    length = len(sign_data)
    print(length)
    print 'sign_data: ',sign_data
    print obj.verify(raw_data,sign_data)


if __name__=='__main__':
    main()