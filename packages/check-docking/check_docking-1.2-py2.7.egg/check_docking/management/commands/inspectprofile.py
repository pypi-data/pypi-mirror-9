#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""生成配置文件, 检测依赖该配置文件进行.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/06'

import os
from django.conf import settings
from django.utils.importlib import import_module
from django.core.management.base import NoArgsCommand
from check_docking.utility import UrlApi


class Command(NoArgsCommand):
    help = "make data_config.py profile file of inspect request data."

    def handle_noargs(self, **options):
        setting_module = os.environ.get("DJANGO_SETTINGS_MODULE")
        project_catalog = os.path.dirname(import_module(setting_module).__file__)

        # noinspection PyUnresolvedReferences
        check_config = getattr(settings, "INSPECT_PROFILE", None)

        # 判读存在且不为空, 且符合格式为"项目.模块"命名, 结尾不能带后缀.
        if check_config and check_config.count('.') > 0 and not check_config.endswith('.py'):
            gen_file = os.path.join(project_catalog, '%s.py' % check_config.split('.')[-1])
        else:
            gen_file = os.path.join(project_catalog, "check_config.py")

        UrlApi(gen_file).gen_interfaces()
