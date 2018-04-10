#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/15
# discription :tag length value
# vision      :
# copyright   :All copyright reserved by FMSH company
from __future__ import division, absolute_import, print_function, unicode_literals
__author__ = 'zuodengbo'
from collections import OrderedDict
from .data_struct import ELEMENT_FORMAT,render_element,read_tag,is_constructed,Tag
from .raw_elements import Parse


class TLV(dict):
    """tag length value"""

    def unmarshal(self, data):
        tlv = self
        i = 0

        if len(data) < 3:
            #至少3字节
            return data

        while i < len(data):
            tag,tag_len = read_tag(data[i:])
            i += tag_len
            length = data[i]
            i += 1
            value = data[i:i + length]

            if is_constructed(tag[0]):
                value = TLV.unmarshal(value)

            tag = Tag(tag)
            if ELEMENT_FORMAT.get(tag) == Parse.DOL:
                 value = DOL.unmarshal(value)
            elif ELEMENT_FORMAT.get(tag) ==Parse.TAG_LIST:
                value = TagList.unmarshal(value)

            #如果标签重复，放在列表中
            if tag in tlv:
                if type(tlv[tag]) is not list:
                    tlv[tag] = [tlv[tag]]
                tlv[tag].append(value)

            else:
                tlv[tag] = value
            i += length
        return tlv

    def __repr__(self):
        vals = []

        for key,val in self.items():
            out = "\n%s: " % str(key)
            if type(val) in (TLV,DOL) or type(val) is list and len(val) > 0 and type(val[0]) in (TLV,DOL):
                out += str(val)

            else:
                out += render_element(key,val)
            vals.append(out)

        return "{" + (",".join(vals)) + "}"

class DOL(OrderedDict):
    """Data Object List.
       This is sent by the card to the terminal to define a structure for
       future transactions, consisting of an ordered list of data elements and lengths
    """
    @staticmethod
    def unmarshal(self, data):
        #从二进制表示中构造一个dol对象（作为一个字节列表）
        dol = self()
        i = 0
        while i < len(data):
            tag,tag_len = read_tag(data[i:])
            i += tag_len
            length = data[i]
            i += 1
            dol[Tag(tag)] = length

        return dol

    def size(self):
        #结构体大小用字节表示
        return sum(self.values())

    def unserialise(self,data):
        #解析一个字节的输入流作为一个tlv对象
        if self.size() != len(data):
            raise Exception('Incorrect input size (expecting %s bytes, got %s)' % (self.size(),len(data)))

        tlv = TLV()
        i = 0
        for tag,length in self.items():
            tlv[tag] = data[i:i + length]
            i += length

        return tlv

    def serialise(self,data):
        #给定一个tag->value的字典，把这些数据写出来，根据dol，丢失的数据将为null

        output = []
        for tag,length in self.items():
            value = data.get(tag,[0x0] * length)
            if len(value) < length:
                #如果长度比所需的短，左移
                value = [0x0] * (length - len(value)) + value
            elif len(value) > length:
                raise Exception('Data for tag %s is too long' % tag)

            output += value

        assert len(output) == self.size()
        return output

class TagList(list):
    """a list of tags"""
    @staticmethod
    def unmarshal(cls, data):
        tag_list = cls()
        i = 0
        while i < len(data):
            tag,tag_len = read_tag(data[i:])
            i += tag_len
            tag_list.append(Tag(tag))
        return tag_list