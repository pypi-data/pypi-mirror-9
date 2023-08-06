# coding: utf-8

from __future__ import print_function, unicode_literals

from django.db import models


class TemplateQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)
