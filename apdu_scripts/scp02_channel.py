#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
import time
import sys, os
from binascii import *
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard import Exceptions
from smartcard.ATR import ATR
import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
from Crypto.Cipher import DES, DES3

exePath = os.path.split(sys.path[0])[0]
# sys.path[0].replace('\ResetCard.exe','') #Make sure the file dir is correct both in python script and  exe
# Log Setting
LOG_PATH_FILE = os.path.split(sys.path[0])[0] + "\\" + "ResetCard.log"
LOG_MODE = 'a'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10M
LOG_MAX_FILES = 5  # 4 Files: Cap2Cos.log.1, Cap2Cos.log.2, Cap2Cos.log.3, Cap2Cos.log.4
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s %(levelname)-10s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s"
handler = RotatingFileHandler(LOG_PATH_FILE, LOG_MODE, LOG_MAX_SIZE, LOG_MAX_FILES)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)



def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


def loadcfg():
    config = ConfigParser.RawConfigParser()
    # Get config path
    config_path = cur_file_dir()
    try:
        config.read(config_path + '\ResetCard.ini')
        # print (config_path + '\ResetCard.ini')
        if not config.has_section('CARD_INFO'):
            print ("ResetCard.ini has none [CARD_INFO]")
            logger.error('ResetCard.ini has none [CARD_INFO]')
            sys.exit(1)
        if not config.has_section('READER_INFO'):
            print ("ResetCard.ini has none [READER_INFO]")
            logger.error('ResetCard.ini has none [READER_INFO]')
            sys.exit(1)
        if not config.has_section('SETTING_INFO'):
            print ("ResetCard.ini has none [SETTING_INFO]")
            logger.error('ResetCard.ini has none [SETTING_INFO]')
            sys.exit(1)
        if not config.has_section('EXTRA_CMD'):
            print ("ResetCard.ini has none [EXTRA_CMD]")
            logger.error('ResetCard.ini has none [EXTRA_CMD]')
            sys.exit(1)
        g_comcode = config.get('CARD_INFO', 'Card_Comcode')
        g_uid = config.get('CARD_INFO', 'Card_Uid')
        g_vendor = config.get('CARD_INFO', 'Card_vendor')
        reader_restrict = config.get('READER_INFO', 'Auto_Connect')
        reader_from = config.get('READER_INFO', 'Reader_From')
        isd_AID = config.get('SETTING_INFO', 'ISD_AID')
        time_out_1 = config.get('SETTING_INFO', 'Time_Out_1')
        time_out_1 = int(time_out_1)
        time_out_2 = config.get('SETTING_INFO', 'Time_Out_2')
        time_out_2 = int(time_out_2)
        alert = config.get('SETTING_INFO', 'Sound_Alert')
        Batch_Process = config.get('SETTING_INFO', 'Batch_Process')
        command1 = config.get('EXTRA_CMD', 'Command1')
        para1 = config.get('EXTRA_CMD', 'Para1')
        data1 = config.get('EXTRA_CMD', 'Data1')
        extr_cmd_name = config.get('EXTRA_CMD', 'Name1')

        #print g_comcode,g_uid,reader_restrict,reader_from,isd_AID,time_out_1,time_out_2,alert,Batch_Process,command1,para1,data1,extr_cmd_name
        return g_comcode, g_uid, g_vendor, reader_restrict, reader_from, isd_AID, time_out_1, time_out_2, alert, Batch_Process, command1, para1, data1, extr_cmd_name
    except Exception as e:
        print ("load ResetCard.ini failed %s" % e)
        logger.error('load ResetCard.ini failed {0}'.format(e))
        sys.exit(1)


def deal_with_list(instr):
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


def generate_session_key(constant, seq_counter, static_key):  # page
    assert len(constant) == 4
    assert len(seq_counter) == 4
    assert len(static_key) == 32
    derivation_data = constant + seq_counter + '00' * 12
    cipher_3DES = DES3.new(unhexlify(static_key), DES3.MODE_CBC, unhexlify('00' * 8))
    sk = cipher_3DES.encrypt(unhexlify(enc_des_padding(derivation_data)))
    return hexlify(sk)[:32]


def generate_card_cryptogram(host_challenge, seq_counter, card_challenge, session_key, ):
    assert len(host_challenge) == 16
    assert len(seq_counter) == 4
    assert len(card_challenge) == 12
    data = host_challenge + seq_counter + card_challenge + '8000000000000000'
    assert len(data) == 48
    cipher_3DES = DES3.new(unhexlify(session_key), DES3.MODE_CBC, unhexlify('00' * 8))
    card_cryptogram = hexlify(cipher_3DES.encrypt(unhexlify(data)))
    assert len(card_cryptogram) == 48
    return card_cryptogram[32:48]


def verify_card_cryptogram(card_cryptogram, seq_counter, host_challenge, card_challenge, static_key):
    session_key = generate_session_key('0182', seq_counter, static_key)  # triple-DES in CBC mode
    assert len(session_key) == 32
    cc = generate_card_cryptogram(host_challenge, seq_counter, card_challenge, session_key).upper()
    if cc == card_cryptogram:
        return 1
    else:
        return 0


def generate_host_cryptogram(seq_counter, card_challenge, host_challenge, key):
    data = seq_counter + card_challenge + host_challenge + '8000000000000000'
    assert len(data) == 48
    sk = generate_session_key('0182', seq_counter, key)
    assert len(sk) == 32
    cipher_3DES = DES3.new(unhexlify(sk), DES3.MODE_CBC, unhexlify('00' * 8))
    host_cryptogram = hexlify(cipher_3DES.encrypt(unhexlify(data)))
    assert len(host_cryptogram) == 48
    return host_cryptogram[32:48]


def generate_key_check_value(key):
    data = '0000000000000000'
    data = mac_des_padding(data)
    cipher_DES = DES3.new(unhexlify(key), DES3.MODE_ECB, unhexlify('00' * 8))
    s_keycheckvalue = hexlify(cipher_DES.encrypt(unhexlify(data)))
    return s_keycheckvalue[:6].upper()


def generate_data_encrypt_decrypt(seq_counter, data, key, mode=0):
    sk = generate_session_key('0181', seq_counter, key)
    assert len(sk) == 32
    # print(sk)
    cipher_3DES = DES3.new(unhexlify(sk), DES3.MODE_ECB, unhexlify('00' * 8))
    if mode == 0:
        enc_data = hexlify(cipher_3DES.encrypt(unhexlify(data)))
        return enc_data.upper()
    else:
        dec_data = hexlify(cipher_3DES.decrypt(unhexlify(data)))
        return dec_data.upper()


def mac_des_padding(apdu):
    assert len(apdu) % 2 == 0
    apdu = apdu + '80'
    length = len(apdu) / 2
    r = length % 8
    if r == 0:
        return apdu.upper()
    else:
        apdu = apdu + '00' * (8 - r)
        return apdu.upper()


def enc_des_padding(apdu):
    assert len(apdu) % 2 == 0
    apdu = apdu + '80'
    # return apdu
    length = len(apdu) / 2
    r = length % 8
    if r == 0:
        return apdu.upper()
    else:
        apdu = apdu + '00' * (8 - r)
        return apdu.upper()


def generate_retail_mac(seq_counter, key, ICV, apdu):
    apdu = mac_des_padding(apdu)
    sk = generate_session_key('0101', seq_counter, key)
    sk1 = sk[0:16]
    sk2 = sk[16:32]
    cipher_DES = DES.new(unhexlify(sk1), DES.MODE_CBC, unhexlify(ICV))
    temp = cipher_DES.encrypt(unhexlify(apdu))
    temp = hexlify(temp)[-16:]
    cipher_DES1 = DES.new(unhexlify(sk1), DES.MODE_ECB)
    cipher_DES2 = DES.new(unhexlify(sk2), DES.MODE_ECB)
    temp = cipher_DES2.decrypt(unhexlify(temp))
    temp = cipher_DES1.encrypt(temp)
    return hexlify(temp).upper()


def generate_apdu_mac(seq_counter, key, ICV, apdu):
    apdu = mac_des_padding(apdu)
    sk = generate_session_key('0101', seq_counter, key)
    sk1 = sk[0:16]
    sk2 = sk[16:32]
    if ICV != '0000000000000000':
        cipher_DES_ICV = DES.new(unhexlify(sk1), DES.MODE_ECB, unhexlify('0000000000000000'))
        ICV = hexlify(cipher_DES_ICV.encrypt(unhexlify(ICV)))
    cipher_DES = DES.new(unhexlify(sk1), DES.MODE_CBC, unhexlify(ICV))
    temp = cipher_DES.encrypt(unhexlify(apdu))
    temp = hexlify(temp)[-16:]
    cipher_DES1 = DES.new(unhexlify(sk1), DES.MODE_ECB)
    cipher_DES2 = DES.new(unhexlify(sk2), DES.MODE_ECB)
    temp = cipher_DES2.decrypt(unhexlify(temp))
    temp = cipher_DES1.encrypt(temp)
    return hexlify(temp)


def send_apdu(APDU_hex, mask):
    APDU = deal_with_list(APDU_hex)
    if mask != "":
        print("-->APDU : " + mask)
        logger.debug("-->APDU : {0} ".format(mask))
    else:
        print("-->APDU : " + str(toHexString(APDU)).replace(" ", ""))
        logger.debug("-->APDU : {0} ".format(str(toHexString(APDU)).replace(" ", "")))
    response, sw1, sw2 = cardservice.connection.transmit(APDU)
    response_str = str(toHexString(response)).replace(" ", "")
    sw = combine_sw1_sw2(sw1, sw2)
    if response_str == '':
        print('<--APDU : ' + sw + " (" + check_sw(sw) + ")")
        logger.debug("<--APDU : {0} ".format(sw))
    else:
        print ('<--APDU : ' + response_str + ' ' + sw + " (" + check_sw(sw) + ")")
        logger.debug("<--APDU : {0} {1} ".format(response_str, sw))

    if sw1 == 0x6C:
        APDU[4] = sw2
        response, sw1, sw2 = cardservice.connection.transmit(APDU)
        print ("-->APDU : " + str(toHexString(APDU)).replace(" ", ""))
        logger.debug("-->APDU : {0} ".format(str(toHexString(APDU)).replace(" ", "")))
        response_str = str(toHexString(response)).replace(" ", "")
        sw = combine_sw1_sw2(sw1, sw2)
        if response_str == '':
            print ('<--APDU : ' + sw + " (" + check_sw(sw) + ")")
            logger.debug("<--APDU : {0} ".format(sw))
        else:
            print('<--APDU : ' + response_str + ' ' + sw + " (" + check_sw(sw) + ")")
            logger.debug("<--APDU : {0} {1} ".format(response_str, sw))
    elif sw1 == 0x61:
        GET_RESPONSE = '00C0000000'
        GET_RESPONSE = GET_RESPONSE[:-2] + padding_sw(sw2)
        Get_Response = deal_with_list(GET_RESPONSE)
        response, sw1, sw2 = cardservice.connection.transmit(Get_Response)
        print("-->APDU : " + str(toHexString(Get_Response)).replace(" ", ""))
        logger.debug("-->APDU : {0} ".format(str(toHexString(APDU)).replace(" ", "")))
        response_str = str(toHexString(response)).replace(" ", "")
        sw = combine_sw1_sw2(sw1, sw2)
        if response_str == '':
            print('<--APDU : ' + sw + " (" + check_sw(sw) + ")")
            logger.debug("<--APDU : {0} ".format(sw))
        else:
            print('<--card : ' + response_str + ' ' + sw + " (" + check_sw(sw) + ")")
            logger.debug("<--card : {0} {1} ".format(response_str, sw))

    return response_str, sw1, sw2


def padding_sw(sw):
    h_padded_sw = str(hex(sw))[2:].upper()
    h_padded_sw = (2 - len(h_padded_sw)) * '0' + h_padded_sw
    return h_padded_sw


def combine_sw1_sw2(sw1, sw2):
    return padding_sw(sw1) + padding_sw(sw2)


def check_sw(sw):
    sw_codes = {'9000': 'Success',
                '6581': 'Memory wrong!',
                '6200': 'Logical channel has been closed!',
                '6283': 'warning!CARD_LOCKED!',
                '6400': 'No specific issues!',
                '6700': 'Lc len wrong!',
                '6881': 'not support logical channel!',
                '6982': 'not meet the security status!',
                '6985': 'not meet the use conditions!',
                '6A86': 'P1,P2 wrong!',
                '6D00': 'not support cmd!',
                '6E00': 'not support Category!',
                '6A88': 'Can not find the data!',
                '6A82': 'Can not find the app!',
                '6A84': 'Out of memory!',
                '6A80': 'Error in cmd!',
                '6A81': 'not support function!',
                '9484': 'Not support algorithm!',
                '9485': 'Invalid key checksum value!',
                '61**': '61 XX',
                '6C**': '6C XX!'
                }
    if len(sw) != 4:
        return 'Wrong SW length!'
    else:
        try:
            if sw[:2] == '61':
                sw2 = sw[2:]
                sw = sw[:2] + '**'
                return sw_codes[sw].replace('XX', 'XX,Get more data '.format(sw2))
            elif sw[:2] == '6C':
                sw2 = sw[2:]
                sw = sw[:2] + '**'
                return sw_codes[sw].replace('XX', 'XX,Err LC,resend APDU '.format(sw2))
            else:
                return sw_codes[sw]
        except Exception as e:
            return 'Unknow SW : ' + sw


def open_SCP02_channel():
    # SELECT
    send_apdu(SELECT, "")

    # InitialUpdate
    data, sw1, sw2 = send_apdu(InitialUpdate, "")
    # Deal with data
    key_diversification_data = data[0:20]
    key_info = data[20:24]
    sequence_counter = data[24:28]
    card_challenge = data[28:40]
    card_cryptogram = data[40:56]

    ret = verify_card_cryptogram(card_cryptogram, sequence_counter, host_challenge, card_challenge, default_key)
    assert ret == 1
    host_cryptogram = generate_host_cryptogram(sequence_counter, card_challenge, host_challenge, default_key)

    # print('mac_ICV '+ mac_ICV)
    if securitylevel == 0:
        # print(sequence_counter,default_key,mac_ICV,'8482000010'+host_cryptogram)
        retail_mac = generate_retail_mac(sequence_counter, default_key, mac_ICV, '8482000010' + host_cryptogram)
        send_apdu('8482000010' + host_cryptogram + retail_mac, "")
    elif securitylevel == 1:
        # print(sequence_counter,default_key,mac_ICV,'8482010010'+host_cryptogram)
        retail_mac = generate_retail_mac(sequence_counter, default_key, mac_ICV, '8482010010' + host_cryptogram)
        send_apdu('8482010010' + host_cryptogram + retail_mac, "")
    elif securitylevel == 3:
        # print(sequence_counter,default_key,mac_ICV,'8482030010'+host_cryptogram)
        retail_mac = generate_retail_mac(sequence_counter, default_key, mac_ICV, '8482030010' + host_cryptogram)
        send_apdu('8482030010' + host_cryptogram + retail_mac, "")
    else:
        print("Invalid securitylevel {0}".format(securitylevel))
    return retail_mac, sequence_counter


def get_secured_apdu(APDU, ICV, sequence_counter):
    # print('get_secured_apdu start')
    int_Lc = 0
    if len(APDU) > 10:
        int_Lc = int(APDU[8:10], 16) * 2 + 10
        APDU = APDU[:int_Lc]
    else:
        APDU = APDU

    if securitylevel == 0:
        return APDU, ICV
    else:
        # print('APDU before Mod : '+ APDU)
        APDU = '84' + APDU[2:8] + padding_sw((len(APDU[10:]) + 16) / 2) + APDU[10:]
        # print('84', APDU[2:8] , padding_sw((len( APDU[10:])+ 16 )/2) ,APDU[10:])
        # print('APDU after Mod : '+ APDU)
        # print((sequence_counter,default_key,ICV,APDU))
        # retail_mac = generate_retail_mac(sequence_counter,default_key,ICV,APDU)
        retail_mac = generate_apdu_mac(sequence_counter, default_key, ICV, APDU)

        # print (retail_mac)
        # print(securitylevel)

    if securitylevel == 1 or int_Lc == 0:  # 若Lc为00,则不加密,仅计算C-MAC后发送
        APDU = (APDU + retail_mac).upper()
        # print('get_secured_apdu end')
        return APDU, retail_mac
    else:  # 若Lc不为0且securitylevel=3,则发送密文带C-MAC的报文
        sk = generate_session_key('0182', sequence_counter, default_key)
        assert len(sk) == 32
        # sk_cbc = sk[0:16]
        cipher_DES3 = DES3.new(unhexlify(sk), DES.MODE_CBC, unhexlify("0000000000000000"))
        encrypt_apdu = hexlify(cipher_DES3.encrypt(unhexlify(enc_des_padding(APDU[10:]))))
        # print(encrypt_apdu.upper())
        leng = len(encrypt_apdu + retail_mac)
        APDU = ('84' + APDU[2:8] + hex(leng / 2)[2:] + encrypt_apdu + retail_mac).upper()
        # print('get_secured_apdu end')
        return APDU, retail_mac


if __name__ == '__main__':


    print (time.asctime())

    # Load config
    g_comcode_c, g_uid_c, g_vendor, reader_restrict, reader_from, isd_AID, time_out_1, time_out_2, alert, batch_process, command1, para1, data1, extr_cmd_name = loadcfg()

    # Set basic APDUs
    SELECT = '00A4040000'
    CLEAR_CARD = '80FE000000'
    Get_Response = '00C0000000'

    host_challenge = '1122334455667788'  # TO-DO： get random data from random-lib
    InitialUpdate = '8050000008' + host_challenge

    default_key = '404142434445464748494a4b4c4d4e4f'
    IV = '0000000000000000'
    mac_ICV = '0000000000000000'
    sequence_counter = '0000'

    readerList = []
    if reader_from == '1':
        UserSettings = exePath + "\\" + "UserSettings.etdl"
        print(UserSettings)
        f = open(UserSettings, 'r')  # get user settings
        lnum = 0
        for line in f:
            lnum += 1
            sStr1 = line
            sStr0 = 'ReleasablePcscApduPCO'
            if sStr1.find(sStr0) > 0:
                sStr1 = line
                sStr2 = '="'
                sStr1 = sStr1[sStr1.find(sStr2) + 2:]
                sStr3 = '");'
                sStr1 = sStr1[:sStr1.find(sStr3)]
                print(sStr1)
                break
            else:
                continue
        readerList.append(sStr1)
    else:
        readerList = readers()
    logger.debug("Reset Card in those Reader : {0} ".format(readerList))
    cardtype = AnyCardType()
    cardrequest = CardRequest(readers=readerList, timeout=time_out_1, cardType=cardtype)

    do_extra = 1
    if command1 == 'FMSH':
        command1 = '80FE'
    elif command1 == 'NULL':
        do_extra = 0

    program_title = '{0} for {1}'.format(para1.replace('_', ' '), g_vendor)
    if para1 == 'RESET_CARD':
        para1 = '0000'
    elif para1 == 'SET_DTRRTR':
        para1 = '000B'
    lc1 = str(hex(len(data1) / 2)).replace("x", "")

    while (1):
        print(program_title)
        print("Mode {0}".format(batch_process))

        # Step1 重启并获取ATR中的UID、comcode值等
        logger.debug('Card ReseT Starting...')
        try:
            cardservice = cardrequest.waitforcard()
            cardservice.connection.connect()
            print ('<--card ATR : ' + str(toHexString(cardservice.connection.getATR())).replace(" ", ""))
            logger.debug('<--card : {0} '.format(str(toHexString(cardservice.connection.getATR())).replace(" ", "")))
        except Exceptions as ex:
            logger.error('<--get card ATR fail:{0}'.format(ex))
            print(ex)
        ATR = str(toHexString(cardservice.connection.getATR())).replace(" ", "")

        if ATR[0:4] == '3B68':
            g_comcode = ATR[-16:-8]
            g_uid = ATR[-8:]
        elif ATR[0:4] == '3B8B':
            g_comcode = ATR[-18:-8]
            g_uid = ATR[-10:-2]
        else:
            g_comcode = g_comcode_c
            g_uid = g_uid_c
        logger.debug('Card Reset Finished...')

        # Step2 清卡指令，或者其他自定义指令
        if do_extra == 1:
            # 执行额外操作
            cmd_name = '{0} of {1}'.format(extr_cmd_name, g_vendor)
            print(command1 + para1 + lc1 + data1)
            data, sw1, sw2 = send_apdu(command1 + para1 + lc1 + data1, cmd_name)
            data = ''

        ##Step3 卡片清理/特殊指令后的操作
        time.sleep(time_out_2)

        print('Delay for %d micro seconds and %d seconds' % (time_out_1, time_out_2))

        # card_reset()
        logger.debug('Card Reset Starting...')
        try:
            cardrequest = CardRequest(readers=readerList, timeout=time_out_1, cardType=cardtype)
            cardservice = cardrequest.waitforcard()
            cardservice.connection.connect()
            print('<--card : ' + str(toHexString(cardservice.connection.getATR())).replace(" ", ""))
            logger.debug(
                '<--card ATR : {0} '.format(str(toHexString(cardservice.connection.getATR())).replace(" ", "")))
        except Exceptions as ex:
            logger.error('<--get card ATR fail:{0}'.format(ex))
        logger.debug('Card Reset Finished...')
        # send_apdu('00A4040000','Set ATS')
        securitylevel = 0
        open_SCP02_channel()
        send_apdu('80E2800012EC10107880A002209000' + g_comcode + g_uid, 'Set ATS')
        send_apdu('80E280000FEB0D3B78180001' + g_comcode + g_uid, 'Set ATR')

        print('80E2800010EB0D3B78180001' + g_comcode + g_uid)
        securitylevel = 1
        retail_mac, sequence_counter = open_SCP02_channel()
        # new_apdu,retail_mac = get_secured_apdu('80E2800018EB0D3B78180001' + g_comcode + g_uid,retail_mac,sequence_counter)
        new_apdu, retail_mac = get_secured_apdu('80E2800010EB0D3B78180001AABBCCDD3737373737', retail_mac,
                                                sequence_counter)
        print(new_apdu)
        print('securitylevel = 1')
        send_apdu(new_apdu, '')

        securitylevel = 3
        retail_mac, sequence_counter = open_SCP02_channel()
        new_apdu, retail_mac = get_secured_apdu('80E2800020EB0D3B78180001' + g_comcode + g_uid, retail_mac,
                                                sequence_counter)
        print(new_apdu)
        print('securitylevel = 3')
        send_apdu(new_apdu, '')

        # if set_elfaid == 1 :
        #    data,sw1,sw2 = send_apdu('80E280000F FD01 ' + ELFAID,"")#set ELF AID
        # if set_emaid == 1 :
        #    data,sw1,sw2 = send_apdu('80E280000F FD02 ' + EMAID,"")#set EMAID
        send_apdu(SELECT, "")  # Set ISD AID if Needed
        if g_vendor != "FMSH":  # 删除Romify Applet
            open_SCP02_channel()
            send_apdu('80E40080094F0747656E6572616C', 'Extra Init Command')
            send_apdu('80E400800A4F0850424f435f444343', 'Extra Init Command')
        if data[8:24] != isd_AID:
            open_SCP02_channel()
            send_apdu('80E280000A4F08' + isd_AID, 'Change ISD AID')  # Change ISD AID
            send_apdu('00A4040008' + isd_AID, 'Verify AID')  # Verify AID

        securitylevel = 3
        retail_mac, sequence_counter = open_SCP02_channel()
        new_apdu, retail_mac = get_secured_apdu('80F0800700', retail_mac, sequence_counter)
        new_apdu, retail_mac = get_secured_apdu('80F0800F00', retail_mac, sequence_counter)
        new_apdu, retail_mac = get_secured_apdu('80F28000024F0000', retail_mac, sequence_counter)
        print('securitylevel = 3')
        send_apdu(new_apdu, '')

        # End of process

        print(time.asctime())
        if alert == "1":
            print('\a' * 7)  # An alert sound from PC)

        if batch_process != '1':
            if batch_process == '2':  # 手动执行
                raw_input('press enter key to exit')
            break
        else:  # 配置为批量清卡模式，间隔time_out_2 秒即重复进行清卡。
            print('请准备更换卡片')
            i = 0
            for i in range(time_out_2):  # 倒计时
                time.sleep(1)
                time_out_3 = time_out_2 - i
                print(time_out_3)
                i = i + 1

    logger.debug("Finish Card Reset")
    sys.exit()
