# coding:utf8

"""
Created on 2014-07-06

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import cPickle
import json


class Serializable(object):
    """序列化接口

    提供两个基本的方法loads和dumps，序列化和反序列化时只作用于对象的公有属性，对于下划线开头的属性认定为私有属性。
    """

    def loads(self, s):
        raise NotImplementedError

    def dumps(self):
        raise NotImplementedError


class CPickleSerializable(Serializable):

    def loads(self, s):
        obj = cPickle.loads(s)
        if not isinstance(obj, self.__class__):
            raise TypeError("object type load by cPickle is not: %s" % self.__class__)
        for name in self.__dict__:
            if not name.startswith('_'):
                setattr(self, name, getattr(obj, name))

    def dumps(self):
        return cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL)


class JsonSerializable(Serializable):

    def loads(self, s):
        dct = json.loads(s)
        for name in self.__dict__:
            if not dct.has_key(name):
                raise TypeError("load json data error. miss attribute: %s" % name)
            setattr(self, name, dct.get(name))

    def dumps(self):
        dct = dict()
        for name in self.__dict__:
            if not name.startswith('_'):
                dct[name] = getattr(self, name)
        return json.dumps(dct)