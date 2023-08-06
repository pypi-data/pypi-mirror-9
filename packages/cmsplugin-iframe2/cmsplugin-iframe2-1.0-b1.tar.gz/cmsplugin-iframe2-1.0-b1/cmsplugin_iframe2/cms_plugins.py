from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from .models import IFramePlugin

@plugin_pool.register_plugin
class IFramePlugin(CMSPluginBase):
    model = IFramePlugin
    name = _('IFrame')
    text_enabled = True
    render_template = 'cmsplugin_iframe2/iframe.html'

