# -*- coding: utf-8 -*-
"""

    tatoo_cli.signals
    ~~~~~~~~~~~~~~~~~

    Signals defined by tatoo-cli.

"""

from tatoo.utils.dispatch import Signal

#: Sent when the umbrella command is ready to be extended.
register_subcommands = Signal()  # pylint: disable=C0103
