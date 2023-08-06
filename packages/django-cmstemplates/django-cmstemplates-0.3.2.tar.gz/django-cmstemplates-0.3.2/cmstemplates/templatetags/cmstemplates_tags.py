# coding: utf-8

from __future__ import print_function, unicode_literals

from django import template

from cmstemplates import queries as q


register = template.Library()


@register.simple_tag(takes_context=True)
def cms_group(context, group_name):
    template_group = q.get_template_group(group_name)
    content = q.get_cached_content_for_group(template_group)
    return template.Template(content).render(context)
