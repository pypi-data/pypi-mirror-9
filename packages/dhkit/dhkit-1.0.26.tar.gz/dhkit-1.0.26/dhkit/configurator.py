#coding:utf8

"""
Created on 2014-05-26

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import ConfigParser


class ConfigError(Exception):
    """
    """


class Configurator(object):

    @classmethod
    def parse_complex_config(cls, parser, section, key, complex_type):
        if isinstance(complex_type, dict) or isinstance(complex_type, list) or isinstance(complex_type, tuple):
            value = parser.get(section, key)
            try:
                return eval(value)
            except:
                raise ConfigError("parse complex type value error. key: %s" % key)
        else:
            raise ConfigError("unsupport configuration type.")

    @classmethod
    def parse_simple_list_config(cls, parser, section, key, py_value):
        """对简单列表类型进行配置，列表中值必须为float basestring int boolean中其一

        sample:
            [biz]
            card_bin = 001, 002, 003

        对应配置config为：
            biz = {
                'card_bin': ['001', '002', '003'],
            }
        """
        v = parser.get(section, key)
        v_list = v.split(",")

        if len(v_list) != len(py_value):
            raise ConfigError("list configuration error.")

        list_value = []
        for i in range(0, len(py_value)):
            pv = py_value[i]
            pv_type = type(pv)
            if pv_type not in (unicode, str, int, float, bool):
                raise ConfigError("unsupport list configuration type.")
            try:
                list_value.append(pv_type(v_list[i].strip()))
            except ValueError:
                raise ConfigError("list value configuration error")
        return list_value

    @classmethod
    def parse_simple_dict_config(cls, parser, section, key, py_value):
        """对简单字典类型进行配置，配置文件可以配置一级字典，value的值必须为float basestring int boolean中其一

        sample:
            [biz]
            wallet.deposit_account = 622080980933022
            wallet.branch_no = 100233

        对应配置config为：
            biz = {
                'wallet': {
                    'deposit_account': '622080980933022',
                    'branch_no': 100233,
                }
            }
        """
        k_list = key.split(".")
        if len(k_list) != 2:
            raise ConfigError("dict configuraton error")

        sub_key = k_list[1]
        dict_value = py_value.copy()
        if sub_key in dict_value.keys():
            pv_type = type(dict_value.get(sub_key))
            if pv_type not in (unicode, str, int, float, bool):
                raise ConfigError("unsupport dict value configuration type.")
            try:
                dict_value[sub_key] = pv_type(parser.get(section, key))
            except ValueError:
                raise ConfigError("dict value configuration error")
        return dict_value

    @classmethod
    def load(cls, filename):
        parser = ConfigParser.ConfigParser()
        if not parser.read(filename):
            raise ConfigError("can not read config file:%s" % filename)
        import types
        cfgs = dict()
        for (k, v) in cls.__dict__.items():
            if type(v) is types.FunctionType or k.startswith('_'):
                continue
            cfgs[k] = v
        for (cfg, cfg_dct) in cfgs.items():
            if parser.has_section(cfg):
                for (k, v) in cfg_dct.items():
                    nv = cls._get_config(parser, cfg, k, v)
                    if nv is not None:
                        cfg_dct[k] = nv

    @classmethod
    def _get_config(cls, parser, section, key, py_value):
        options = parser.options(section)
        has_option = False
        dict_option = False
        dict_value = py_value
        for option in options:
            if option.startswith(key + ".") and isinstance(py_value, dict):
                dict_option = True
                dict_value = cls.parse_simple_dict_config(parser, section, option, dict_value)
            elif option == key:
                has_option = True
        if dict_option:
            return dict_value
        if not has_option:
            return None
        if isinstance(py_value, basestring):
            return parser.get(section, key)
        elif isinstance(py_value, bool):
            return parser.getboolean(section, key)
        elif isinstance(py_value, int):
            return parser.getint(section, key)
        elif isinstance(py_value, float):
            return parser.getfloat(section, key)
        elif isinstance(py_value, list):
            return cls.parse_simple_list_config(parser, section, key, py_value)
        elif isinstance(py_value, tuple):
            return tuple(cls.parse_simple_list_config(parser, section, key, py_value))
        else:
            raise ConfigError("unsupport configuration type.")

