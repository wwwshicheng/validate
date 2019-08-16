# @File  : validate.py
# @Author: wsc
# @Date  : 2019/8/7
# @Desc  :

import datetime
import json
import re
import time
from collections import Iterable
from json import JSONDecodeError

from libs.common import Struct


def argument(self, **kw):
    args = Struct()
    error = None
    for k, typ in kw.items():
        if not isinstance(typ, Schema):
            raise TypeError()
        v = self.get(k)
        try:
            typ.key = k
            args[k] = typ.validate(v)
        except Exception as e:
            error = str(e)
    return args, error


class Schema(object):
    """
    使用方法
    """

    def __init__(self, typ, required=False, default=None, f=None, error=None, key=None):
        self.type = typ
        self.default = default
        self.required = required
        self.filter = f
        self._error = error
        self.key = key
        self.child_key = None

    def val_error(self, message):
        if self.child_key:
            message = f'{self.key}: {self.child_key} {message}'
        else:
            message = f'{self.key}: {message}'
        return self._error or message

    def _iterable_parse(self, val, typ=None):
        """可迭代格式验证"""
        try:
            val = json.loads(val) if isinstance(val, str) else val
        except JSONDecodeError:
            raise TypeError(self.val_error("格式转换错误"))

        if not isinstance(val, Iterable):
            raise TypeError(self.val_error("不是数组格式"))

        self._required(val)
        data = []
        _typ = self.type if not typ else typ
        for i in _typ:
            for v in val:
                v = self._validate_method(v, i)
                data.append(v)
        return data or val

    def _type_parse(self, val, typ):
        """可转换格式验证"""
        try:
            val = typ(val)
        except ValueError:
            raise ValueError(self.val_error("类型转换错误"))
        return val

    def _dict_parse(self, val, typ):
        """dict格式验证"""
        if not isinstance(val, dict):
            try:
                val = json.loads(val)
            except TypeError:
                raise TypeError(self.val_error("json.loads error"))
            except JSONDecodeError:
                raise TypeError(self.val_error("转换错误"))

        self._required(val)
        keys = typ.keys()
        data = Struct()
        for i in keys:
            if i not in val.keys():
                raise TypeError("%s中缺少key: %s" % (self.key, i))
        for k, v in val.items():
            self.child_key = k
            t = typ.get(k)
            if not t:
                data[k] = v
            else:
                data[k] = self._validate_method(v, t)
        return data or Struct(val)

    def _callable(self, data, func):
        """可调用方式验证"""
        if not callable(func):
            raise TypeError("%s 过滤器不支持调用" % self.key)
        return func(data)

    @staticmethod
    def _date_parse(date, _):
        try:
            date = int(date)
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date))
        except ValueError:
            if len(date.split()) > 1:
                fmt = "%Y-%m-%d %H:%M:%S"
                slices = 3
            else:
                fmt = "%Y-%m-%d"
                slices = 3
            t = time.strptime(date, fmt)
            return datetime.datetime(*t[:slices])

    def _timestamp(self, date, _):
        if not date:
            return 0
        try:
            if len(date.split()) > 1:
                v = time.strptime(date, "%Y-%m-%d %H:%M:%S")
                v = int(time.mktime(v))
            else:
                t = time.strptime(date, "%Y-%m-%d")
                v = int(time.mktime(t))
        except Exception as _:
            import traceback
            traceback.print_exc()
            raise TypeError("%s 时间戳转换错误" % self.key)
        return v

    def _re(self, data, typ):
        rp = re.compile(typ)
        mh = rp.match(data)
        if mh:
            return mh.group()
        else:
            raise TypeError("%s 正则匹配错误" % self.key)

    def _validate_method(self, val, typ):
        med = {
            TYPE: self._type_parse,
            ITERABLE: self._iterable_parse,
            DICT: self._dict_parse,
            DATE: self._date_parse,
            TIMESTAMP: self._timestamp,
            CALLABLE: self._callable
        }.get(_priority(typ), self._re)
        return med(val, typ)

    def _required(self, val):
        if val is None:
            if not self.required:
                return self.default if self.default else type_default_value(self.type)
            else:
                raise TypeError("%s 不能为空" % self.key)

    def validate(self, val):
        if val is None:
            if not self.required:
                return self.default if self.default else type_default_value(self.type)
            else:
                raise TypeError("%s 不能为空" % self.key)
        if self.filter:
            if not self._callable(val, self.filter):
                raise TypeError("参数%s: 不合法" % self.key)
        data = self._validate_method(val, self.type)
        return data


def _callable_str(callable_):
    if hasattr(callable_, '__name__'):
        return callable_.__name__
    return str(callable_)


RE, CALLABLE, TYPE, DICT, ITERABLE, DATE, TIMESTAMP = range(7)


def _priority(s):
    """Return priority for a given object."""
    if type(s) in (list, tuple, set, frozenset):
        return ITERABLE
    if type(s) is dict:
        return DICT
    if issubclass(type(s), type):
        return TYPE
    if callable(s):
        return CALLABLE
    if isinstance(s, str):
        if s == "date":
            return DATE
        if s == "timestamp":
            return TIMESTAMP
        return RE


def type_default_value(t):
    """返回基本类型默认值, 没有识别的类型返回None"""
    if type(t) in (list, tuple, set, frozenset):
        return []
    if type(t) is dict:
        return {}
    return {str: "", int: 0}.get(t)
