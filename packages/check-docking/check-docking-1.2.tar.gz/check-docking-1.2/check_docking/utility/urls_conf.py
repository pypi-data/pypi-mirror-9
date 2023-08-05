# !/usr/bin/env python
# -*- coding: utf-8 -*-

u"""从指定urls.py文件中读取REST API地址, 生成url数据相关文件.

    仅针对django项目, 其它项目需要修改适配标识, 与request.get_full_path()相比, 缺少斜杠.
    用于对REST API的客户端参数传入验证; 用于对某项接口的数据组装.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/01/20'

import os
import os.path
from datetime import datetime

import six


class UrlConfig(object):
    """生成url配置文件
    """

    def __init__(self, src_file, gen_file, flag=False, fmt='list', func=False):
        """
            :param src_file: 源urls.py文件路径.
            :param gen_file: 生成文件存放路径.
            :param flag:    是否带正则全部生成.
            :param fmt:     生成数据格式, ['list','dict']其中之一.
            :param func:    是否读附带对应的函数名, 仅fmt='dict'时生效.
        """

        self._srcfile = src_file
        self._gen_file = gen_file
        self._flag = flag
        self._fmt = fmt
        self._func = func

    def read_url_from_file(self, variable=None):
        """从源码urls.py里读取所有url行.

            :param variable: 变量名称.
            适配形式: "url(r'^user/$',"
        """

        prefix = "url(r'^"
        suffix = "$',"
        url_list = []

        # 检查传入生成格式
        if self._fmt not in ['list', 'dict']:
            six.print_(u'无效的生成格式输入.')
            return

        # 检查源传入真实有效性
        if not os.path.exists(self._srcfile):
            six.print_(u'无效的文件路径输入.')
            return

        # 检查存传入真实有效性
        if not os.path.exists(os.path.dirname(self._gen_file)):
            os.makedirs(os.path.dirname(self._gen_file))

        with open(self._srcfile, 'rb') as urls:
            lines = urls.readlines()

            with open(self._gen_file, 'wb') as f:
                f.write('# !/usr/bin/env python\n')
                f.write('# coding=utf-8\n\n')

                now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(r'"""该文件由工具 %s 生成, 生成时间 %s."""' % (os.path.basename(__file__), now_time))

                if not variable:
                    variable = 'rest_api_url'

                if self._fmt == 'list':
                    f.write('\n\n%s = [\n' % variable)
                elif self._fmt == 'dict':
                    f.write('\n\n%s = {\n' % variable)

                for line in lines:
                    try:
                        line = line.strip()  # 去空字符
                        if line.startswith(prefix):  # 以前缀起始
                            url = line[len(prefix):line.index(suffix)]  # 截得url

                            def get_func_name(str_line):
                                """获取函数名
                                """
                                func_name = str_line[str_line.index(suffix) + len(suffix):].strip().strip("'),")
                                func_name_list = func_name.split(".")

                                # 排除: TemplateView.as_view(
                                if func_name.find("(") < 0:
                                    return func_name_list[-1]
                                else:
                                    return None

                            if self._flag:
                                if self._fmt == 'list':
                                    f.write("    '%s',\n" % url)
                                elif self._fmt == 'dict':
                                    f.write("    '%s': {},\n" % url)
                            else:
                                if url.count('?') == 0:  # 不要含参地址
                                    if self._fmt == 'list':
                                        f.write("    '%s',\n" % url)
                                    elif self._fmt == 'dict':
                                        if self._func:

                                            # 特殊情况跳出该条
                                            func = get_func_name(line)
                                            if func is None:
                                                continue

                                            f.write("    '%s': '%s',\n" % (url, func))
                                        else:
                                            f.write("    '%s': {},\n" % url)

                            url_list.append(url)

                    except (ValueError, Exception):  # 跳过index()错误行
                        continue

                if self._fmt == 'list':
                    f.write(']\n')
                elif self._fmt == 'dict':
                    f.write('}\n')

        return url_list
