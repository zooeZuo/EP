#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/19
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
from __future__ import division, absolute_import, print_function, unicode_literals
__author__ = 'zuodengbo'
from apdu_scripts.command_apdu import (SelectFile, GetApplicationVersion, StoreData,
                                       GetChallenge, GetApplicationInformation, CreditForLoad, InitializeForLoad, Extradition)
from transmit import TransmissionProtocol

class Card(object):
    def __init__(self,connection):
        self.tp = TransmissionProtocol(connection)

    def get_ADF(self):
        """Get ADF file by AID or FID"""
        res = self.tp.exchange(SelectFile)
        if res.p1 == 04:
            assert 5 <= len(res.data) <= 16
            return self.tp.exchange(SelectFile(AID = 0xA000000003869807010))
        elif res.p1 == 00:
            assert len(res.data) == 2
            return self.tp.exchange(SelectFile(FID = 0x3F01))

    def get_application_version(self):
        """
        :return:
        """

        return self.tp.exchange(GetApplicationVersion())

    def store_data(self,obj,personal_data):
        """
        :param obj:
        :param personal_data:
        :return:
        """

        return self.tp.exchange(StoreData(obj,personal_data))

    def get_challenge(self):
        """
        :return:
        """
        return self.tp.exchange(GetChallenge())

    def get_application_information(self):
        """
        :return:
        """
        return self.tp.exchange(GetApplicationInformation())

    def initialize_for_load(self):
        """
        :return:
        """
        return self.tp.exchange(InitializeForLoad())

    def credit_for_load(self):
        """
        :return:
        """
        return self.tp.exchange(CreditForLoad())

    def extradition(self):
        """
        :return:
        """
        return self.tp.exchange(Extradition())