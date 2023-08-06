# coding: utf-8

from __future__ import print_function, unicode_literals

from django.core.cache import cache

from cmstemplates import models as m


def active_templates_for_group(group):
    return list(group.templates.active().order_by('weight'))


def get_template_group(name):
    group, _ = m.TemplateGroup.objects.get_or_create(name=name)
    return group


def get_content_for_group(group):
    templates = active_templates_for_group(group)

    content = []
    for template in templates:
        content.append(template.render())

    return ''.join(content)


def get_cached_content_for_group(group):

    content = cache.get(group.cache_key)

    if content is not None:
        return content

    content = get_content_for_group(group)
    cache.set(group.cache_key, content)

    return content
