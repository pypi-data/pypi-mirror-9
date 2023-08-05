#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""接口文档的定义入库, 目前使用django ORM 做数据集中存储方式.
    结合 django.contrib.admin, 也为数据管理提供操作入口.
"""

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/06'

from check_docking.stored.django.models import Interface, Method, DataItem