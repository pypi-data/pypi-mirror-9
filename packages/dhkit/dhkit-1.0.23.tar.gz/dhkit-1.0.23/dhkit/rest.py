# coding:utf8

"""
Created on 2014-10-14

@author: tufei
@description: 基于Tornado框架实现的RESTFul形式的API
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import sys
import json
import functools
import types
import tornado.web
import tornado.gen
import httplib
import dhkit.error
import dhkit.fields
from dhkit import log

try:
    from tornado.concurrent import is_future
except ImportError:
    from tornado.concurrent import Future
    def is_future(x):
        return isinstance(x, Future)


class RestError(dhkit.error.Error):

    httpcode = 500

    def __init__(self, msg=None):
        code = self.cls_code - self.httpcode
        super(RestError, self).__init__(msg, code)

    def to_dict(self):
        return dict(return_code=self.code, return_message=self.message)


class BadRequestError(RestError):

    httpcode = httplib.BAD_REQUEST


class NotFoundError(RestError):

    httpcode = httplib.NOT_FOUND


class UnAuthorizedError(RestError):

    httpcode = httplib.UNAUTHORIZED


class ForbiddenError(RestError):

    httpcode = httplib.FORBIDDEN


class MethodNotAllowedError(RestError):

    httpcode = httplib.METHOD_NOT_ALLOWED


def method_decorator(func):
    @functools.wraps(func)
    @tornado.gen.coroutine
    def decorator(self, *args, **kwargs):
        try:
            if self.request.method in ('PUT', 'POST', 'PATCH'):
                self._load_json_body()
            self.check_arguments()
            self.check_authenticated()
            _func = tornado.gen.coroutine(func)
            result = yield _func(self, *args, **kwargs)
            if result is not None:
                self.write(result)
        except dhkit.fields.ArgumentError, e:
            raise BadRequestError(e.message)
        except RestError:
            raise
        except Exception:
            log.exception("System internal exception")
            raise RestError("System internal exception. please contact administrator")
        finally:
            if self.ALLOW_CORS:
                self.set_cors_headers()

    return decorator


class RestMeta(type):

    DECORATOR_METHODS = ('get', 'post', 'head', 'put', 'delete', 'patch')

    def __new__(mcs, name, bases, dct):
        members = dct.items()
        for name, member in members:
            if type(member) is types.FunctionType and name in mcs.DECORATOR_METHODS:
                dct[name] = method_decorator(member)
        return type.__new__(mcs, name, bases, dct)


class RestRequestHandler(tornado.web.RequestHandler):
    """RESTful形式的RequestHandler

    The HTTP request methods are typically designed to affect a given resource in standard ways:
    ----------------------------------------------------------------------------------------------
    |HTTP Method|Action					|Examples
    ----------------------------------------------------------------------------------------------
    |GET		|Obtain information 	|http://example.com/api/orders
    |      		|about a resource		|(retrieve order list)
    ----------------------------------------------------------------------------------------------
    |GET		|Obtain information		|http://example.com/api/orders/123
    |			|about a resource		|(retrieve order #123)
    ----------------------------------------------------------------------------------------------
    |POST		|Create a new resource	|http://example.com/api/orders
    |			|						|(create a new order, from data provided with the request)
    ----------------------------------------------------------------------------------------------
    |PUT		|Update a resource		|http://example.com/api/orders/123
    |			|						|(update order #123, from data provided with the request)
    ----------------------------------------------------------------------------------------------
    |DELETE		|Delete a resource		|http://example.com/api/orders/123
    |			|						|(delete order #123)
    ----------------------------------------------------------------------------------------------
    """

    __metaclass__ = RestMeta

    ALLOW_CORS = True

    ACCESS_CONTROL_ALLOW_HEADERS = [
        'Origin',
        'No-Cache',
        'X-Requested-With',
        'If-Modified-Since',
        'Pragma',
        'Last-Modified',
        'Cache-Control',
        'Expires',
        'Content-Type',
        'X-E4M-With',
    ]

    ARGCHKS_GET = []

    ARGCHKS_POST = []

    ARGCHKS_PUT = []

    ARGCHKS_PATCH = []

    ARGCHKS_DELETE = []

    def options(self, *args, **kwargs):
        self.set_header('Allow', ','.join(self.SUPPORTED_METHODS))

    def check_arguments(self):
        self._checked_arg_dict = dict()
        if self.request.method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
            return
        request_arguments = [] + self.request.arguments.keys()
        argchk_dict = self.get_argchk_dict(self.request)
        for arg_name in argchk_dict:
            arg_value = self.get_argument(arg_name, None)
            field = argchk_dict.get(arg_name)
            self._checked_arg_dict[arg_name] = field.validate(arg_value)
            if arg_name in request_arguments:
                request_arguments.remove(arg_name)

        # 将不在检查列表的参数也加入参数列表中
        for arg_name in request_arguments:
            if arg_name not in argchk_dict:
                self._checked_arg_dict[arg_name] = self.get_argument(arg_name, None)

    def get_parameter(self, name, default=None):
        """获取HTTP请求的参数，包括查询参数和Body参数

        和get_argument方法不同的是，get_parameter获取的是已经验证检查过的参数字典
        :param name: 参数名称
        :param default: 默认值
        :return: 参数值，返回类型取决于Field中定义的类型
        """
        return self._checked_arg_dict.get(name, default)

    def get_first_path_argument(self):
        """获取在URL路由中定义的第一个正则匹配的路径参数
        :return:
        """
        if self.path_args:
            return self.path_args[0]
        elif self.path_kwargs:
            keys = self.path_kwargs.keys()
            return self.path_kwargs.get(keys[0])
        else:
            raise RuntimeError("Can not find path argument from path: %s" % self.request.path)

    @classmethod
    def get_argchk_dict(cls, request):
        if '__argchks' not in vars(cls):
            cls.__argchks = {}

        if request.method in cls.__argchks:
            return cls.__argchks[request.method]

        method_argchk_dict = dict()
        argchks = getattr(cls, 'ARGCHKS_%s' % request.method)
        for field in argchks:
            method_argchk_dict[field.name] = field
        cls.__argchks[request.method] = method_argchk_dict
        return method_argchk_dict

    def return_back(self, chunk):
        raise tornado.gen.Return(chunk)

    def set_cors_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', ','.join(self.SUPPORTED_METHODS))
        self.set_header('Access-Control-Allow-Headers', ','.join(self.ACCESS_CONTROL_ALLOW_HEADERS))

    def write(self, chunk):
        if isinstance(chunk, (dict, list)):
            chunk = self.encode_body(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        super(RestRequestHandler, self).write(chunk)

    def _handle_request_exception(self, e):
        if isinstance(e, RestError):
            self.log_exception(*sys.exc_info())
            self.write(e.to_dict())
            self.set_status(e.httpcode)
            if not self._finished:
                self.finish()
            return
        super(RestRequestHandler, self)._handle_request_exception(e)

    def log_exception(self, typ, value, tb):
        # if isinstance(value, RestError) and value.httpcode >= 500:
        #     log.error("System Exception: %s" % value.message, exc_info=(typ, value, tb))
        super(RestRequestHandler, self).log_exception(typ, value, tb)

    def _load_json_body(self):
        try:
            json_body = self.decode_body(self.request.body)
            if not isinstance(json_body, (dict, list)):
                raise TypeError
            self.request.json_body = json_body
        except Exception:
            raise BadRequestError("method: %s request body must be a json body" % self.request.method)

    def _execute(self, transforms, *args, **kwargs):
        if 'OPTIONS' not in self.SUPPORTED_METHODS:
            if isinstance(self.SUPPORTED_METHODS, tuple):
                self.SUPPORTED_METHODS = self.SUPPORTED_METHODS + ('OPTIONS',)
            else:
                self.SUPPORTED_METHODS.append('OPTIONS')
        super(RestRequestHandler, self)._execute(transforms, *args, **kwargs)

    # def _execute_method(self):
    #     if not self._finished:
    #         self._when_complete(self._wrap_method(), self._execute_finish)

    def check_authenticated(self):
        """Overrided by subclass, default do nothing
        """
        pass

    def encode_body(self, body):
        """默认使用JSON序列化
        """
        return json.dumps(body)

    def decode_body(self, body):
        """默认使用JSON反序列化
        """
        return json.loads(body)