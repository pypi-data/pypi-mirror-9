# !/usr/bin/env python
# coding=utf-8

u"""对传入的request data 检测模块.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/01/20'

import sys
import six
import traceback
from functools import wraps
from django.conf import settings
from django.utils.importlib import import_module


def request_data_inspect(request):
    """客户传入值验证处理模块, web handle调用.

        :param request: 请求对象

        步骤:
            检查请求方法是否错误.
            检查必传项是否缺失.

            检查传入项是否存在.
            检查传入项数据类型.
    """

    message = None
    url_path = request.get_full_path().lstrip('/')
    url_method = request.method
    url_data = rest_api_url[url_path]

    if url_method in url_data:
        message = 'kylin: request method error.'
    else:
        dict_data = getattr(request, url_method)
        if len(dict_data) > 0:

            # 检查必传项是否缺失
            for (key, value) in url_data[url_method].items():
                if value['must'] and key not in dict_data.keys():
                    message = 'kylin: [%s] must data item missing.' % key

            # 检查传入项是否合法
            for (key, value) in dict_data.items():
                if key not in url_data[url_method]:
                    message = 'kylin: [%s] invalid incoming parameter.' % key
                else:
                    if type(value) != url_data[url_method][key]['type']:
                        message = 'kylin: [%s] invalid data type.' % key

    six.print_(message)
    return message


def request_inspect(request):
    """给装饰函数使用的一种方式.

        控制阀门的一种方式.
    """

    if getattr(settings, "IS_DATA_INSPECT", None):
        return request_data_inspect(request)

    return None


def debug_request(func=None):
    u"""检测view函数, 非middleware, 用decorator方式.

        :param func: view 函数

        settings.py items DEBUG = True:

    """

    if settings.DEBUG:

        @wraps(func)
        def returned_wrapper(request, *args, **kwargs):
            try:
                # 检验传入数据
                message = request_inspect(request)
                if message:
                    return message

                response = func(request, *args, **kwargs)
                return response

            except Exception as e:
                six.print_(e)
                traceback.print_exc(file=sys.stdout)

        return returned_wrapper
    else:
        pass


def get_check_config():
    u"""获取检测依赖配置数据
    """

    check_config = getattr(settings, "INSPECT_PROFILE", None)
    if check_config:
        try:
            project_catalog = import_module(check_config)
            return project_catalog.REST_API_URL
        except ImportError:
            raise ImportError("ImportError: No module named check_config, please usage: 'manage.py inspectprofile'.")


rest_api_url = get_check_config()
