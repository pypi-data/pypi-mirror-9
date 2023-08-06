# -*- coding: utf-8 -*-
"""

    tatoo_cli.interfaces
    ~~~~~~~~~~~~~~~~~~~~

    Interfaces defined in tatoo-cli.

"""

from __future__ import absolute_import, unicode_literals

from zope.interface import Interface, Attribute


class IOutputter(Interface):

    name = Attribute('Outputter name.')

    def format(result):
        """Returns string representing the formatter result."""
