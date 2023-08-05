# !/usr/bin/env python
# coding=utf-8

u"""检测中间件."""

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/06'

from django import http
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from check_docking.inspect import request_data_inspect


class InspectMiddleware(object):
    """检测请求参数的中间件, 在settings.py配置项MIDDLEWARE_CLASSES中增加.
    """

    def __init__(self):
        """要求务必是在调试模式下启用.
        """

        # 调试模式下且IS_DATA_INSPECT开启下有效.
        if not all((settings.DEBUG, getattr(settings, "IS_DATA_INSPECT", None))):
            raise MiddlewareNotUsed

    def process_view(self, request, view, args, kwargs):
        message = request_data_inspect(request)
        if message:
            response = http.HttpResponse(message)
            return response
