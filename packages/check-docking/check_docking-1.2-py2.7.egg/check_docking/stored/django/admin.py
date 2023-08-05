#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'kylinfish@126.com'
__date__ = '2015/02/06'

from django.contrib import admin
from check_docking.stored.django.models import Interface, Method, DataItem


class DataItemInline(admin.StackedInline):
    """数据
    """
    model = DataItem


class MethodInline(admin.StackedInline):
    """方法
    """
    model = Method
    inlines = [DataItemInline]


class InterfaceAdmin(admin.ModelAdmin):
    u"""自定义ModelAdmin.
    """

    list_display = ('url_path', 'def_name', 'created_at', 'updated_at', )

    ordering = ('-created_at',)
    list_filter = ('updated_at', )
    search_fields = ('url_path', 'def_name', )
    inlines = [MethodInline]


class MethodAdmin(admin.ModelAdmin):
    u"""自定义ModelAdmin.
    """

    list_display = ('used_interface', 'name_method', 'created_at', 'updated_at', )
    ordering = ('-created_at',)
    list_filter = ('updated_at', )
    search_fields = ('used_interface__url_path', 'used_interface__def_name',)
    inlines = [DataItemInline]


class DataItemAdmin(admin.ModelAdmin):
    u"""自定义ModelAdmin.
    """

    list_display = ('used_method', 'data_name', 'data_type', 'data_must', 'data_value', 'created_at', 'updated_at', )
    ordering = ('-created_at',)
    list_filter = ('updated_at', )
    search_fields = ('used_interface__url_path', 'used_interface__def_name',)

# admin.site.register(Method)
# admin.site.register(DataItem)
# admin.site.register(Interface)

admin.site.register(Method, MethodAdmin)
admin.site.register(DataItem, DataItemAdmin)
admin.site.register(Interface, InterfaceAdmin)
