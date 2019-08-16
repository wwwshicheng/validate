# @File  : common.py
# @Author: wsc
# @Date  : 2019/8/12
# @Desc  :
from django.http import JsonResponse


class Struct(dict):
    """
    - 为字典加上点语法. 例如:
    >>> o = Struct({'a':1})
    >>> o.a
    >>> 1
    >>> o.b
    >>> None
    """

    def __init__(self, *e, **f):
        if e:
            self.update(e[0])
        if f:
            self.update(f)

    def __getattr__(self, name):
        # Pickle is trying to get state from your object, and dict doesn't implement it.
        # Your __getattr__ is being called with "__getstate__" to find that magic method,
        # and returning None instead of raising AttributeError as it should.
        if name.startswith('__'):
            raise AttributeError
        return self.get(name)

    def __setattr__(self, name, val):
        self[name] = val

    def __delattr__(self, name):
        self.pop(name, None)

    def __hash__(self):
        return id(self)


def fail_response(data="", message="", code=-1):
    """错误响应"""
    resp = dict(
        code=code,
        data=data,
        message=message
    )
    return JsonResponse(data=resp)


def ok_response(data="", message="", code=0):
    """正常响应"""
    resp = dict(
        code=code,
        data=data,
        message=message
    )
    return JsonResponse(data=resp)
