# !/usr/bin/env python
# coding=utf-8

"""测试"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/01/20'

import os
import os.path
import sys
import six
from check_docking.utility import UrlApi
from check_docking.utility import FromURL, FromRequest

# project root directory
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")


def gen_inspect_config():
    """从数据库生成检测用的配置文件
    """

    # noinspection PyUnresolvedReferences
    gen_file = os.path.join(base_path, "project", "data_config.py")
    UrlApi(gen_file).gen_interfaces()


def gen_from_url():
    """从django项目urls.py搜索service接口.
    """

    # noinspection PyUnresolvedReferences
    source_file = os.path.join(base_path, 'project', 'urls.py')
    # noinspection PyUnresolvedReferences
    create_file = os.path.join(base_path, "project", "data_source.py")

    url_data = FromURL(source_file, create_file)
    url_data.gen_data_source()

    try:
        from project_demo.project.data_source import rest_api_url
    except ImportError:
        rest_api_url = None
        six.print_('please first usage: FromURL(source_file, create_file).gen_data_source()')

    url_data.get_data_source(rest_api_url)


def gen_from_request():
    """从django项目源码搜索service接口参数.
    """
    # noinspection PyUnresolvedReferences
    code_file = [os.path.join(base_path, 'demo', 'handles.py'), os.path.join(base_path, 'demo', 'views.py')]
    # noinspection PyUnresolvedReferences
    code_data = os.path.join(base_path, 'project', 'data_params.py')

    param_data = FromRequest(code_file, code_data)
    param_data.gen_data_request()

    try:
        from project_demo.project.data_params import rest_api_url
    except ImportError:
        rest_api_url = None
        six.print_('please first usage: FromRequest(code_file, code_data).gen_data_request()')

    param_data.save_data_request(rest_api_url)


if __name__ == '__main__':
    """执行操作.
    """

    six.print_(u'Beginning...')

    gen_inspect_config()
    gen_from_url()
    gen_from_request()

    six.print_(u'Finished')