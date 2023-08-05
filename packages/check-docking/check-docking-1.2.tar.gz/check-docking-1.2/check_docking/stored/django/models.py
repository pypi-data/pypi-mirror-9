#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/06'

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Interface(models.Model):
    """REST API 接口类.

        属性: url地址, 函数名
    """

    url_path = models.CharField(_('request path'), max_length=50, unique=True)
    def_name = models.CharField(_('function name'), max_length=50)
    status = models.BooleanField(_('status'), default=True)
    created_at = models.DateTimeField(_('created datetime'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated datetime'), auto_now=True)

    class Meta:
        db_table = u'check_docking_interface'
        verbose_name = _('interface')
        verbose_name_plural = _('interface list')

    def __unicode__(self):
        return "%s : %s" % self.natural_key()

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.url_path, self.def_name


class Method(models.Model):
    """REST API 接口所使用的方法.

        属性: 归属接口, 方法类型.
    """

    METHODS = (
        (0, u'None'),
        (1, u'GET'),
        (2, u'POST'),
        (3, u'PUT'),
        (4, u'DELETE'),
        (5, u'HEAD'),
        (6, u'TRACE'),
        (7, u'CONNECT'),
        (8, u'OPTIONS'),
    )

    @classmethod
    def get_method_id(cls, key):
        """获取方法ID
        """
        method_id = None
        for method in cls.METHODS:
            if method[1] == key:
                method_id = method[0]
                break
        return method_id

    used_interface = models.ForeignKey(Interface, verbose_name=_('used interface'), related_name='support_methods')
    name_method = models.IntegerField(_('method name'), choices=METHODS, default=0)

    created_at = models.DateTimeField(_('created datetime'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated datetime'), auto_now=True)

    class Meta:
        db_table = u'check_docking_method'
        verbose_name = _('interface method')
        verbose_name_plural = _('interface method list')
        unique_together = (("used_interface", "name_method"),)

    def __unicode__(self):
        return "%s : %s" % self.natural_key()

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.used_interface.def_name, self.METHODS[int(self.name_method)][1]


class DataItem(models.Model):
    """REST API 接口所使用的某方法参数列表.

        属性: 归属接口方法, 传入参数key, 参数类型, 是否必填项, 如果非必填项默认值.
    """

    TYPES = (
        (0, u'None'),
        (1, u'str'),
        (2, u'int'),
        (3, u'float'),
    )

    used_method = models.ForeignKey(Method, verbose_name=_('used method'))
    data_name = models.CharField(_('data name'), max_length=50)
    data_type = models.IntegerField(_('data type'), max_length=50, choices=TYPES, default=0)
    data_must = models.BooleanField(_('data must'), default=False)
    data_value = models.CharField(_('data default value'), max_length=50, null=True, blank=True, default=None)

    created_at = models.DateTimeField(_('created datetime'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated datetime'), auto_now=True)

    class Meta:
        db_table = u'check_docking_data_item'
        verbose_name = _('interface data item')
        verbose_name_plural = _('interface data item list')
        unique_together = (("used_method", "data_name"),)

    def __unicode__(self):
        return "%s : %s" % self.natural_key()

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.used_method, self.data_name
