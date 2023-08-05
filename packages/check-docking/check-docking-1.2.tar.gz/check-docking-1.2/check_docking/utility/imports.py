# !/usr/bin/env python
# coding=utf-8

u"""从源码中搜索资源, 导入数据库.

    usage:
        FromURL         搜索接口.
        FromRequest     搜索提交数据参数.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/01/20'

import pprint

import six

from check_docking.utility.urls_conf import UrlConfig
from check_docking.utility.urls_data import CollectSource
from check_docking.stored import Interface, Method, DataItem


class FromURL(object):
    """从Django项目urls.py中搜索REST API接口.

        搜索, 结果生成一个文件.
        导入, 结果导入数据库里.
    """

    def __init__(self, source_file, create_file):
        """
            :param source_file: urls文件路径.
            :param create_file: 生成文件路径.
        """

        self._source_file = source_file
        self._create_file = create_file

        # flag: 是否带正则全部生成.
        # fmt:  生成数据格式, ['list','dict']其中之一.
        # func: 是否读附带对应的函数名, 仅fmt='dict'时生效.

        self.flag = True
        self.fmt = 'dict'
        self.func = True

    def gen_data_source(self):
        """从urls.py提取service接口地址, 生成数据源文件.
        """

        data_source = UrlConfig(src_file=self._source_file, gen_file=self._create_file,
                                flag=self.flag, fmt=self.fmt, func=self.func)

        data_source.read_url_from_file()

    @staticmethod
    def get_data_source(rest_api_url):
        """导入urls.py数据到库.
        """

        if not rest_api_url:
            six.print_('please first usage: FromURL(source_file, create_file).gen_data_source()')

        for key, value in rest_api_url.iteritems():
            print key, value

            try:
                interface = Interface(url_path=key, def_name=value)
                interface.save()
            except Exception as e:
                six.print_(e)
                continue


class FromRequest(object):
    """从源码中搜索请求参数.
    """

    def __init__(self, code_file, param_file, log_file):
        """
            :param code_file: 代码文件路径集.
            :param param_file: 生成文件路径.
            :param log_file: 日志文件路径.
        """

        self._code_file = code_file
        self._param_file = param_file
        self._log_file = log_file

    def gen_data_request(self):
        """从源码文件中搜索请求参数, 生成数据源.
        """

        my_instance = CollectSource(src_file=self._code_file, gen_file=self._param_file)
        my_instance.gen_data_request()

    @staticmethod
    def save_data_request(self, rest_api_url, debug=False):
        """获取参数数据导入到库.
        """

        if not rest_api_url:
            six.print_('please first usage: FromRequest(code_file, code_data).gen_data_request()')

        # called, but not in rest_api_url
        # 被调用, 但在rest_api_url没数据.
        log_fun_no_data_list = []

        # 处理并汇总函数调用的数据
        for value in rest_api_url.values():
            func_called = value.get('call', None)
            if func_called:
                for func in func_called:
                    if func in rest_api_url:
                        value['GET'] = list(set(value['GET'] + rest_api_url[func]['GET']))
                        value['POST'] = list(set(value['POST'] + rest_api_url[func]['POST']))
                    else:
                        log_fun_no_data_list.append(func)

                del value['call']

        if debug:
            pprint.pprint(rest_api_url)
            return

        interfaces = Interface.objects.all()

        log_api_import_list = []  # 成功的列表日志
        for interface in interfaces:
            six.print_(interface)
            if interface.def_name in rest_api_url:
                url_data = rest_api_url[interface.def_name]  # 接口下数据
                try:
                    for method in url_data.keys():
                        new_method = Method(used_interface=interface, name_method=Method.get_method_id(method))
                        new_method.save()
                        method_data = url_data[method]  # 方法下数据
                        for item in method_data:
                            new_item = DataItem(used_method=new_method, data_name=item)
                            new_item.save()
                except Exception as e:
                    six.print_(e)

                log_api_import_list.append(interface.def_name)

        # 记录保存日志
        with open(self._log_file, 'wb') as f:
            f.write("# called, but not in rest_api_url")
            f.write("# 被调用, 但在rest_api_url没数据.")
            f.write("log_fun_no_data_list:\n\n")
            f.write('\t%s\n' % '\n\t'.join(list(set(log_fun_no_data_list))))

            f.write("# 成功的列表日志")
            f.write("\n\nlog_api_import_list:\n\n")
            f.write('\t%s\n' % '\n\t'.join(list(set(log_api_import_list))))

            f.write("# 余下未导入的列表日志")
            f.write("\n\nlog_api_remain_list:\n\n")
            log_api_remain_list = list(set(rest_api_url.keys()) - set(log_api_import_list))
            f.write('\t%s\n' % '\n\t'.join(log_api_remain_list))
