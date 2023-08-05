# coding:utf8

"""
Created on 2014-08-11

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""


class Error(Exception):
    """异常基类

    异常基类默认有一个类属性cls_code，如果需要自定的错误码，可以在初始化时给一个关键字参数：code
    for example:
    error = Error("This is a error", code=-1008)
    """
    cls_code = -1000

    ERROR_CODE_MAP = {-1000: "系统内部错误"}

    def __init__(self, msg=None, code=None):
        self.msg = msg if msg is not None else ''
        self.code = code or self.cls_code

    message = property(lambda self: self.msg or self.ERROR_CODE_MAP.get(self.code))

    args = property(lambda self: (self.msg, self.code))