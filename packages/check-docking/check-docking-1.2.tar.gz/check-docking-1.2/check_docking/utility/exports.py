# !/usr/bin/env python
# coding=utf-8

u"""从数据源stored生成接口文档的配置文件.

    usage:
        UrlApi(gen_file).gen_interfaces()
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/01/20'

import os
import os.path
from datetime import datetime

from check_docking.stored import Interface, Method, DataItem


class UrlApi(object):
    u"""生成待检测配置文件.
    """

    def __init__(self, gen_file):
        """
            :param gen_file: 生成文件路径.
        """

        self._gen_file = gen_file

    def gen_interfaces(self):
        u"""获取启用的所有接口.
        """

        interfaces = Interface.objects.filter(status=True)
        if interfaces:
            with open(self._gen_file, 'wb') as f:
                now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write('# !/usr/bin/env python\n')
                f.write('# coding=utf-8\n\n')
                f.write(r'"""该文件由工具 %s 生成, 生成时间 %s."""' % (os.path.basename(__file__), now_time))
                f.write('\n\nREST_API_URL = {\n')
                for interface in interfaces:
                    method_data = self.__gen_methods(interface)
                    f.write("    '%s': {%s},\n" % (interface.url_path, method_data))

                f.write('}\n')

    def __gen_methods(self, interface):
        u"""获取指定接口的支持方法.
        """

        methods = Method.objects.filter(used_interface=interface)
        methods_data = []

        for method in methods:
            data_items = self.__gen_data_items(method)
            method_data = "'%s': {%s}" % (Method.METHODS[method.name_method][1], data_items)
            methods_data.append(method_data)

        if methods_data:
            return ', '.join(methods_data)
        else:
            return ''

    @staticmethod
    def __gen_data_items(method):
        u"""获取指定接口支持方法的数据集.
        """

        data_items = DataItem.objects.filter(used_method=method)
        items_data = []

        for item in data_items:
            method_data = "'%s': {'type': '%s', 'must': %s, 'default': '%s'}" % \
                          (item.data_name, DataItem.TYPES[item.data_type][1], item.data_must, item.data_value)
            items_data.append(method_data)

        if items_data:
            return ', '.join(items_data)
        else:
            return ''
