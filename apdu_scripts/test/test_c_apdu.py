#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
import unittest

from util import unformat_bytes
from ..command_apdu import CAPDU, SelectFile, GetChallenge, CreditForLoad


class TestCAPDU(unittest.TestCase):

    def test_unmarshal(self):
        pdu = CAPDU.unmarshal(unformat_bytes('00 A4 04 00 09 A00000000386980701 00'))
        self.assertIs(type(pdu),SelectFile)
        self.assertEqual(pdu.p1,0x04)
        self.assertEqual(pdu.p2,0x00)
        self.assertEqual(len(pdu.data),0x09)
        self.assertEqual(pdu.le,0x00)

        pdu = CAPDU.marshal(unformat_bytes('00 84 00 00 04'))
        self.assertIs(type(pdu),GetChallenge)
        self.assertEqual(pdu.p1,0x00)
        self.assertEqual(pdu.p2,0x00)
        self.assertEqual(len(pdu.data),None)
        self.assertEqual(pdu.le,0x04)

        pdu = CAPDU.marshal(unformat_bytes('805200000B 20160328 151534 A158557B 04'))
        self.assertIs(type(pdu),CreditForLoad)
        self.assertEqual(pdu.p1,0x00)
        self.assertEqual(pdu.p2,0x00)
        self.assertEqual(len(pdu.data),0x0B)
        self.assertEqual(pdu.le,0x04)