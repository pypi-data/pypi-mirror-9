# coding: utf-8

from __future__ import print_function, unicode_literals

from django.core.cache import cache
from django.db.models import signals

from cmstemplates import models as m


def delete_templategroup_cache(sender, instance, **kwargs):
    cache.delete(instance.cache_key)


def delete_template_templategroup_cache(sender, instance, **kwargs):
    cache.delete(instance.group.cache_key)


signals.post_delete.connect(
    delete_templategroup_cache,
    sender=m.TemplateGroup,
    dispatch_uid='delete_templategroup_cache_post_delete',
)

signals.post_delete.connect(
    delete_template_templategroup_cache,
    sender=m.Template,
    dispatch_uid='delete_template_templategroup_cache_post_delete',
)

signals.post_save.connect(
    delete_templategroup_cache,
    sender=m.TemplateGroup,
    dispatch_uid='delete_templategroup_cache_post_save',
)

signals.post_save.connect(
    delete_template_templategroup_cache,
    sender=m.Template,
    dispatch_uid='delete_template_templategroup_cache_post_save',
)
