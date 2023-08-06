# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from tatoo.extension import Extension
from tatoo.signals import extension_load

from tatoo_cli._version import __version__


@extension_load.connect
def populate_defaults(sender, **kwargs):
    sender.env.settings.add_defaults({
        'CLI_OUTPUTTER': None
    })


ext = Extension('cli', version=__version__)
