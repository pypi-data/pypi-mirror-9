# coding:utf8

"""
Created on 2015-02-02

@author: tufei
@description: 提供API签名和验签功能
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
from copy import copy
import urllib
from dhkit.util import hmac_sha1, urlencode


class Signature(object):

    @classmethod
    def sign(cls, url, params, secret):
        sign_base_data = urllib.quote(url, safe="") + urllib.quote(cls.part_request_params(params, sort=True))
        return hmac_sha1(secret, sign_base_data)

    @classmethod
    def verify(cls, url, params, secret, data):
        if cls._is_empty(data):
            return False
        sign_params = copy(params)
        sign_params.pop('sign', None)
        signed = cls.sign(url, sign_params, secret)
        return signed.lower() == data.lower()

    @classmethod
    def verify_tornado_request(cls, request, params, secret):
        sign_data = params.get('sign')
        url = "%s://%s%s" % (request.protocol, request.host, request.path)
        return cls.verify(url, params, secret, sign_data)

    @classmethod
    def part_request_params(cls, params, sort=False, url_encoding=True):
        """把请求要素按照“参数=参数值”的模式用“&”字符拼接成字符串
        @param params: 请求的参数字典
        @param sort: 是否需要根据key值作升序排列
        @param url_encoding: 是否需要URL编码
        @return 拼接成的字符串
        """
        if sort:
            param_items = sorted(params.iteritems(), key=lambda d: d[0])
        else:
            param_items = params.items()

        if url_encoding:
            return urlencode(param_items)
        else:
            results = []
            for item in param_items:
                results.append("%s=%s" % (item[0], item[1]))
            return '&'.join(results)

    @classmethod
    def _is_empty(cls, s):
        if s is None:
            return True
        if isinstance(s, basestring) and len(s) > 0:
            return False
        else:
            return True