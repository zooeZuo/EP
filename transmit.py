#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/16
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
from __future__ import division, absolute_import, print_function, unicode_literals

__author__ = 'zuodengbo'
import logging
from apdu_scripts.response_apdu import RAPDU
from util import format_bytes


class TransmissionProtocol(object):
    """Transport layer"""

    def __init__(self, connection):

        self.log = logging.getLogger(__name__)
        self.connection = connection
        self.connection.connect()
        assert connection.getProtocol() == connection.T0_protocol
        self.log.info('connected to reader')

    def transmit(self, raw_data):
        """ Send raw data to the card, and receive the reply.

            tx_data should be a list of bytes.

            Returns a tuple of (data, sw1, sw2) where sw1 and sw2
            are the protocol status bytes.
        """
        self.log.debug('Raw_Data: %s', format_bytes(raw_data))
        data, sw1, sw2 = self.connection.transmit(raw_data)
        self.log.debug('Response_Data: %s, SW1: %02x, SW2: %02x', format_bytes(data), sw1, sw2)
        return data, sw1, sw2

    def exchange(self, capdu):
        """Send a command to the card and return the response.

            Accepts a CAPDU object and returns a RAPDU.
        """
        send_data = capdu.marshal()
        data, sw1, sw2 = self.transmit(send_data)

        if sw1 == 0x6C:
            send_data[4] = sw2
            data, sw1, sw2 = self.transmit(send_data)

        while sw1 == 0x61:
            data, sw1, sw2 = self.transmit([0x00, 0xC0, 0x00, 0x00, sw2])
            data = data[:-2] + data

        response = RAPDU.unmarshal(data + [sw1, sw2])
        return response


if __name__ == '__main__':
    apdu = '00A4040009A00000000386980701'
    obj = TransmissionProtocol(apdu)
    r = obj.transmit(apdu)
    print(r)
