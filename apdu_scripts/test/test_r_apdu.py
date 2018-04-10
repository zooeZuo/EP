#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
import unittest
from ..response_apdu import RAPDU,SuccessResponse,ErrorResponse,WarningResponse


class TestRAPDU(unittest.TestCase):
    def test_unmarshal(self):
        pdu = RAPDU.unmarshal([0x90, 0x00])
        self.assertIs(type(pdu), SuccessResponse)

        pdu = RAPDU.unmarshal([0x63, 0xC2])
        self.assertIs(type(pdu), WarningResponse)

        with self.assertRaises(ErrorResponse):
            RAPDU.unmarshal([0x6A, 0x81])