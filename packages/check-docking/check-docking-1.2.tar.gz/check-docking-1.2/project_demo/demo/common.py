#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""local and ring-info code integration.
"""

__author__ = 'kylin'
__date__ = '2014/09/20'

import json

import six
from django.http import HttpResponse


if six.PY3:
    range_ = range
else:
    range_ = xrange


def duct_json(dict_data):
    u"""封装json返回数据.

        :param dict_data
    """

    return HttpResponse(json.dumps(dict_data, ensure_ascii=False))
