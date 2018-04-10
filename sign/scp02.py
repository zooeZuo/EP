#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'

import re
from smartcard.util import toHexString
from Crypto.Cipher import DES3,DES
from Crypto.Cipher.DES3 import MODE_CBC
from Crypto.Cipher.DES import MODE_CBC
from smartcard.System import readers
import sys
import logging
import nonce

class SCP02:

    s_enc = '404142434445464748494A4B4C4D4E4F'
    s_mac = '404142434445464748494A4B4C4D4E4F'
    dek = '404142434445464748494A4B4C4D4E4F'
    def __init__(self):
        pass

    # 过程密钥
    def process_key(self):
        derivation_data1 = '01010000000000000000000000000000'
        c_mac_session_key = DES3.new(self.s_mac,MODE_CBC,derivation_data1)
        logging.debug('c_mac session key: %s' % c_mac_session_key)

        derivation_data2 = '01020000000000000000000000000000'
        r_mac_session_key = DES3.new(self.s_mac,MODE_CBC,derivation_data2)
        logging.debug('r_mac session key: %s' % r_mac_session_key)

        derivation_data3 = '01820000000000000000000000000000'
        s_enc_session_key = DES3.new(self.s_enc,MODE_CBC,derivation_data3)
        logging.debug('s_enc session key: %s' % s_enc_session_key)

        derivation_data4 = '01810000000000000000000000000000'
        s_dek_session_key = DES3.new(self.dek,MODE_CBC,derivation_data4)
        logging.debug('s_dek session key: %s' % s_dek_session_key)

    # 内部认证
    def internal_auth(self):
        S_ENC = self.process_key().s_enc_session_key
        host_challenge = nonce.Terminal_Generator_8()
        card_challenge = nonce.Terminal_Generator_6()
        icv = '0000000000000000'
        d_data = host_challenge + '0000' + card_challenge + '8000000000000000'
        data = d_data.decode('hex')
        host_cryptogram = DES3.new(S_ENC,MODE_CBC,icv).encrypt(data)
        logging.debug('host cryptogram: %s' % host_cryptogram)

    # 外部认证
    def external_auth(self):
        S_ENC = self.process_key().s_enc_session_key
        C_MAC = self.process_key().c_mac_session_key
        length_c_mac = len(C_MAC)
        host_challenge = nonce.Terminal_Generator_8()
        card_challenge = nonce.Terminal_Generator_6()
        icv = '0000000000000000'
        d_data = '0000' + card_challenge + host_challenge + '8000000000000000'
        data = d_data.decode('hex')
        host_cryptogram = DES3.new(S_ENC,MODE_CBC,icv).encrypt(data)

        der_data = '8482010010'+host_cryptogram
        length = len(der_data)
        der_data1 = der_data[:length/2]
        der_data2 = der_data[length/2:]
        icv1 = DES.new(C_MAC[0:length_c_mac/2],MODE_CBC,icv).encrypt(der_data1)
        mac = DES3.new(C_MAC,MODE_CBC,icv1).encrypt(der_data2)
        logging.debug('mac: %s' % mac)