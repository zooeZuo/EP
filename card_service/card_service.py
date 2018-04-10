#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
from smartcard.System import readers
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString


class CardService:
    def __init__(self):
        self.readerList = readers()
        self.cardtype = AnyCardType()
        self.cardrequest = CardRequest(readers=self.readerList, timeout=7000, cardType=self.cardtype)
        self.cardservice = self.cardrequest.waitforcard()

    def connect(self):
        self.cardservice.connection.connect()

    def send_apdu_command(self, apdu_command):
        response, SW1, SW2 = self.cardservice.connection.transmit(self._deal_with_list(apdu_command))
        res = (str(toHexString(response)).replace(" ", ""))
        sw = (self._combine_sw1_sw2(SW1, SW2))
        return res, sw

    @staticmethod
    def _padding_sw(sw):
        h_padded_sw = str(hex(sw))[2:].upper()
        h_padded_sw = (2 - len(h_padded_sw)) * '0' + h_padded_sw
        return h_padded_sw

    def _combine_sw1_sw2(self, SW1, SW2):
        return self._padding_sw(SW1) + self._padding_sw(SW2)

    @staticmethod
    def _deal_with_list(instr):
        if len(instr) % 2 == 0:
            i = 0
            outlist = [int(instr[:2], 16)]
            instr = instr[2:]
            for i in range(1, len(instr) / 2):
                outlist.insert(i, int(instr[:2], 16))
                i = i + 1
                instr = instr[2:]
            outlist.insert(i, int(instr, 16))
            return outlist

    def disconnect(self):
        self.cardservice.connection.disconnect()


if __name__ == "__main__":
    cardService = CardService()
    res1, sw_seid = cardService.send_apdu_command("00A4040000")
    if sw_seid == "9000":
        res_seid, sw1 = cardService.send_apdu_command("80CA9F7F00")
        seid = res_seid[30:38] + res_seid[46:54]
        print seid
    cardService.disconnect()
    cardService = CardService()
    res2, sw_balance = cardService.send_apdu_command("00A40000023F01")
    if sw_balance == "9000":
        res_balance, sw2 = cardService.send_apdu_command("805000020B020000000028124554455410")
        balance = int(res_balance[0:8], 16) - 800
        print balance
    cardService.disconnect()
