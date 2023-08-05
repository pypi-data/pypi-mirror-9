# coding:utf8

"""
Created on 2014-09-11

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import urllib
import gzip
import cStringIO
from tornado.httputil import url_concat


def gzip_compress(content):
    out = cStringIO.StringIO()
    gzipfile = gzip.GzipFile(fileobj=out, mode='w', compresslevel=9)
    gzipfile.write(content)
    gzipfile.close()
    out.seek(0)
    byte = out.read(1)
    byte_arr = []
    while byte:
        byte_arr.append(byte)
        byte = out.read(1)
    return bytearray(byte_arr).decode('iso-8859-1')


def urlencode(kwargs, doseq=0):
    """对参数进行URL编码
    :param kwargs: dict类型，参数列表
    :param doseq: 是否排序
    :return: str 编码之后的字符串
    """
    assert isinstance(kwargs, dict)
    query = dict()
    for name, value in kwargs.iteritems():
        if value is not None:
            query[name] = value
    return urllib.urlencode(query, doseq)


def urlconcat(url, kwargs):
    """连接URL和请求参数
    :param url: str类型 url地址
    :param kwargs: dict类型 请求参数字典
    :return: str 拼接好之后的url字符串
    """
    assert isinstance(kwargs, dict)
    query = dict()
    for name, value in kwargs.iteritems():
        if value is not None:
            query[name] = value
    return url_concat(url, query)
