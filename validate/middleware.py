# @File  : middleware.py
# @Author: wsc
# @Date  : 2019/8/7
# @Desc  :
import json
import logging
import traceback
from json import JSONDecodeError

from django.http import RawPostDataException, HttpResponse, QueryDict
from django.utils.deprecation import MiddlewareMixin

from libs.validate import argument

QueryDict.argument = argument


class AuthenticationMiddleware(MiddlewareMixin):

    @staticmethod
    def process_request(request):
        """请求处理"""
        query = request.GET.copy()
        query.update(request.POST)
        try:
            if request.body:
                # 把body参数合并到QUERY
                body = json.loads(request.body.decode())
                query.update(body)
        except JSONDecodeError:
            pass
        except RawPostDataException:
            pass
        request.QUERY = query
        return

    @staticmethod
    def process_response(request, response):
        """响应处理"""
        return response

    @staticmethod
    def process_exception(request, exception):
        """异常处理"""
        exc = traceback.format_exc()
        path = request.get_full_path()
        host = request.get_host()
        fmt_exc = f"host: {host}\npath: {path}\nargs: {request.QUERY}\n{exc}"
        logging.error(fmt_exc)
        return HttpResponse("处理异常，请稍后再试或联系管理员")
