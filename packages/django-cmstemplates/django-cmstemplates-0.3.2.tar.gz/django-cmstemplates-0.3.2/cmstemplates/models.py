# coding: utf-8

from __future__ import unicode_literals, print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from cmstemplates import managers


@python_2_unicode_compatible
class TemplateGroup(models.Model):
    name = models.CharField(_('Template group name'), max_length=255)
    description = models.TextField(
        _('Short description'), blank=True)

    class Meta:
        verbose_name = _('Template group')
        verbose_name_plural = _('Template groups')

    def __str__(self):
        if self.description:
            return '%s - %s' % (self.name, self.description)
        return self.name

    @property
    def cache_key(self):
        return 'cmstemplates:group:{}'.format(self.name)


@python_2_unicode_compatible
class Template(models.Model):
    name = models.CharField(
        _('Template name'),
        max_length=255,
        help_text=_('Template name, for example, "headline"'),
    )
    group = models.ForeignKey(
        TemplateGroup,
        verbose_name=_('Group'),
        related_name='templates',
    )
    # TODO: add help text in which order output works
    weight = models.IntegerField(_('Output order'), default=0)
    content = models.TextField(_('Content'))
    is_active = models.BooleanField(_('Active'), default=True)
    only_for_superuser = models.BooleanField(
        _('Only for superuser'), default=False)

    objects = managers.TemplateQuerySet().as_manager()

    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = _('Template')
        ordering = ['weight']

    def __str__(self):
        return self.name

    def render(self):
        if self.only_for_superuser:
            html = ''.join([
                '{% if request.user.is_superuser %}',
                self.content,
                '{% endif %}',
            ])
            return html
        return self.content

