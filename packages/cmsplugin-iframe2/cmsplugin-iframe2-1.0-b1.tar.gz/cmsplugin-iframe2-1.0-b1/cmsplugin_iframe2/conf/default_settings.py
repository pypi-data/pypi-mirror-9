from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.utils.translation import ugettext_lazy as _

"""
This file contains default settings for cmsplugin-iframe2
Copy the lines You want to modify into Your project settings
file to override default values.
"""


# set to None to allow any value
CMSPLUGIN_IFRAME_CLASSES = (
    (None, _('no class')),
)

# set to None to allow any value
CMSPLUGIN_IFRAME_WIDTHS = (
    ('200', _('200 pixels')),
    ('400', _('400 pixels')),
    ('800', _('800 pixels')),
    ('100%', _('100 %')),
)

# set to None to allow any value
CMSPLUGIN_IFRAME_HEIGHTS = (
    ('150', _('150 pixels')),
    ('300', _('300 pixels')),
    ('600', _('600 pixels')),
    ('100%', _('100 %')),
)

