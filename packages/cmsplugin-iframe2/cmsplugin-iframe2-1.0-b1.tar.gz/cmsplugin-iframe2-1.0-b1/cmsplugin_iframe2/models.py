# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .conf import settings

class IFramePlugin(CMSPlugin):
    style   = models.CharField(_('style'),  max_length=50,
                help_text=_('value of HTML attribute class'),
                choices=settings.CMSPLUGIN_IFRAME_CLASSES,
                blank=True, null=True)
    width   = models.CharField(_('width'),  max_length=10,
                choices=settings.CMSPLUGIN_IFRAME_WIDTHS,
                blank=True, null=True)
    height  = models.CharField(_('height'), max_length=10,
                choices=settings.CMSPLUGIN_IFRAME_HEIGHTS,
                blank=True, null=True)
    align   = models.CharField(_('align'),  max_length=10,
                choices=(
                    ('left', _('align left')),
                    ('right', _('align right')),
                ), blank=True, null=True)
    src     = models.TextField(_('url'))

