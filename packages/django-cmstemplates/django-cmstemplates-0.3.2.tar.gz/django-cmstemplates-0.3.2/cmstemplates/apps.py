# coding: utf-8

from __future__ import print_function, unicode_literals

from django.apps import AppConfig


class DefaultConfig(AppConfig):
    name = 'cmstemplates'
    verbose_name = 'Шаблоны cmstemplates'

    def ready(self):
        from cmstemplates import signals
