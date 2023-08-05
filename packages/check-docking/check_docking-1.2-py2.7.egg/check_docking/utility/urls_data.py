# !/usr/bin/env python
# -*- coding: utf-8 -*-

u"""从指定源码文件或文件列表读取请求参数列表, 生成数据相关文件.

    仅针对django项目, 其它项目需要修改适配标识.
    仅支持最常用的两种请求方法, GET/POST请求.

    仅支持直接的url view, 以request参数的调用函数能读到, 但传不了url view.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/01/20'

import os
import os.path
import re
from datetime import datetime

import six


class CollectSource(object):
    """从源码中收集各种请求参数.
    """

    METHODS = {'GET': [r"request.GET\[\'(\w*)\'\]"], 'POST': [r"request.POST\[\'(\w*)\'\]"]}

    def __init__(self, src_file, gen_file):
        """
            :param src_file: 源码文件或列表.
            :param gen_file: 数据文件.
        """

        self._source = src_file
        self._gen_file = gen_file

    def gen_data_request(self, variable=None):
        """获取收集数据.

            :param variable: 变量名称.
        """

        # 检查存传入真实有效性
        if not self.__check_path(os.path.dirname(self._gen_file)):
            os.makedirs(os.path.dirname(self._gen_file))

        if self.__check_path(self._gen_file):
            os.remove(self._gen_file)

        if isinstance(self._source, list):
            for srcfile in self._source:
                self.__get_data_file(srcfile, variable)
        else:
            self.__get_data_file(self._source, variable)

    @staticmethod
    def __check_path(file_path):
        """检查源传入真实有效性.

            True:   存在.
            False:  不存在.
        """

        is_flag_exists = False
        if os.path.exists(file_path):
            is_flag_exists = True
        return is_flag_exists

    def __get_data_file(self, srcfile, variable=None):
        """从指定文件中收集数据.

            :param srcfile: 源码文件
            :param variable: 变量名称.
        """

        is_exists = self.__check_path(srcfile)
        if not is_exists:
            six.print_(u'无效的文件路径输入.')
            return

        with open(srcfile, 'rb') as urls:
            if not self.__check_path(self._gen_file):
                with open(self._gen_file, 'wb') as f:
                    f.write('# !/usr/bin/env python\n')
                    f.write('# coding=utf-8\n\n')

                    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(r'"""该文件由工具 %s 生成, 生成时间 %s."""' % (os.path.basename(__file__), now_time))

                    if not variable:
                        variable = 'rest_api_url'
                    f.write('\n\n%s = {\n' % variable)

                    self.__write_data_file(urls, f)
            else:
                with open(self._gen_file, 'ab') as f:
                    self.__write_data_file(urls, f, True)

    def __write_data_file(self, src_fo, gen_fo, footer=False):
        """文件对象数据处理.

            :param src_fo: 源码文件对象.
            :param gen_fo: 生成文件对象.
        """

        # 匹配 def login(request): 或者 def user_detail(request, user_id):
        def_name_re = r"(\w+)\(request(, \w+)?\):"

        def_name_re_called = r"(\w+)\(request(, \w+)*\)"
        def_func_re_called = r"(\w+)\(([A-Za-z0-9_\.]+, )*request.[A-Z]{3,4}(, [A-Za-z0-9_.]+)*\)"

        content = src_fo.read()
        contents = content.split("def ")

        for func in contents:
            # 匹配def_name:
            def_name = None
            def_value = None
            def_names = re.match(def_name_re, func)
            if def_names:
                def_name = def_names.group(1)
                def_value = def_names.group(2)
                # six.print_((def_name, str(def_value).lstrip(", ")))

            if not def_name:
                continue

            data_item_list = []
            for key, values in self.METHODS.iteritems():
                # 匹配def_params
                def_params = []

                if key == "GET" and def_value:  # 处理GET函数参数传递获值类型
                    def_params.append(str(def_value).lstrip(", "))

                for value in values:
                    def_params.extend(re.findall(value, func))

                # six.print_(def_params)

                # 组装method数据
                item = "'%s': %s" % (key, def_params)
                data_item_list.append(item)

            # 匹配 called Function
            def_items_called = []

            # request 作参数传值
            def_names_called = re.findall(def_name_re_called, func)
            for def_name_called in def_names_called:
                if def_name_called and def_name_called[0] != def_name:
                    def_items_called.append(def_name_called[0])

            # request.GET / request.GET 作参数传值.
            def_funcs_called = re.findall(def_func_re_called, func)
            for def_func_called in def_funcs_called:
                if def_func_called:
                    def_items_called.append(def_func_called[0])

            if def_items_called:
                data_item_list.append("'call': %s" % def_items_called)

            api_item = "    '%s': {%s},\n" % (def_name, ', '.join(data_item_list))
            gen_fo.write(api_item)

        if footer:
            gen_fo.write('}\n')
