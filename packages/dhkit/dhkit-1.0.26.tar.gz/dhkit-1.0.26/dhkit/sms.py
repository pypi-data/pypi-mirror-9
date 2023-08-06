# coding:utf8

"""
Created on 2014-10-28

@author: tufei
@description: 提供短信发送功能
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import functools
from urllib import urlencode
from tornado.gen import Return, coroutine
from tornado.util import Configurable
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from xml.etree import ElementTree
from dhkit import log


class Sms(object):

    def __init__(self, **kwargs):
        self._ioloop = IOLoop()
        self._closed = False
        self._async_sms = AsyncSms(**kwargs)

    def close(self):
        if not self._closed:
            self._ioloop.close()
            self._closed = True

    def __del__(self):
        self.close()

    def send(self, phone, content):
        return self._ioloop.run_sync(functools.partial(self._async_sms.send, phone, content))


class AsyncSms(Configurable):

    @classmethod
    def configurable_base(cls):
        return AsyncSms

    @classmethod
    def configurable_default(cls):
        return EmayAsyncSms

    @coroutine
    def send(self, phone, content):
        if isinstance(phone, (list, tuple)):
            resp = yield self.send_multi_impl(phone, content)
        else:
            resp = yield self.send_impl(phone, content)
        raise Return(resp)

    @coroutine
    def send_impl(self, phone, content):
        raise NotImplementedError

    @coroutine
    def send_multi_impl(self, phones, content):
        raise NotImplementedError


class SmsError(Exception):
    """短信异常
    """


class EmayAsyncSms(AsyncSms):

    EMAY_SERVER_URL = 'http://sdk229ws.eucp.b2m.cn:8080/sdkproxy'
    CDKEY = 'CDKEY'
    PASSWORD = 'PASSWORD'

    def initialize(self, base_url=None, cdkey=None, password=None):
        self.base_url = base_url or self.EMAY_SERVER_URL
        self.cdkey = cdkey or self.CDKEY
        self.password = password or self.PASSWORD

    @coroutine
    def send_impl(self, phone, content):
        url = "%s/%s" % (self.base_url, 'sendsms.action')
        params = {
            'cdkey': self.cdkey,
            'password': self.password,
            'phone': phone,
            'message': content,
        }
        resp = yield self._request(url, params)
        raise Return(resp)

    @coroutine
    def send_multi_impl(self, phones, content):
        assert isinstance(phones, (list, tuple))
        resp = yield self.send_impl(','.join(phones), content)
        raise Return(resp)

    @coroutine
    def _register(self):
        url = "%s/%s" % (self.base_url, 'regist.action')
        params = {
            'cdkey': self.cdkey,
            'password': self.password,
        }
        resp = yield self._request(url, params)
        raise Return(resp)

    @coroutine
    def _logout(self):
        url = "%s/%s" % (self.base_url, 'logout.action')
        params = {
            'cdkey': self.cdkey,
            'password': self.password,
        }
        resp = yield self._request(url, params)
        raise Return(resp)

    @coroutine
    def _request(self, url, params):
        http_client = AsyncHTTPClient()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'Keep-Alive',
        }
        body = urlencode(params)
        request = HTTPRequest(url, method='POST', headers=headers, body=body, connect_timeout=10, request_timeout=10)
        log.debug("[SMS REQ] URL: %s body: %s" % (request.url, request.body))
        try:
            response = yield http_client.fetch(request)
            log.debug("[SMS RES] code: %s body: %s" % (response.code, response.body))
            code, message = self._parse_response(response.body)
            if int(code) != 0:
                raise SmsError("获取亿美短信服务错误状态 code:[%s] message:[%s]" % (code, message))
            else:
                raise Return(response.body)
        except HTTPError, ex:
            raise SmsError("调用亿美短信服务失败 code:[%s] message:[%s]" % (ex.code, ex.message))
        except (SmsError, Return):
            raise
        except Exception, ex:
            raise SmsError("调用亿美短信服务异常：%s" % ex.message)

    def _parse_response(self, xml):
        xml = xml.strip()
        root = ElementTree.fromstring(xml)
        code = root.find('error').text
        message = root.find('message').text
        return code, message