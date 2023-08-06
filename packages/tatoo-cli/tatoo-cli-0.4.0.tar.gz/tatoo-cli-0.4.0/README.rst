.. image:: https://badge.fury.io/py/tatoo-cli.png
    :target: http://badge.fury.io/py/tatoo-cli

.. image:: https://travis-ci.org/malinoff/tatoo-cli.svg?branch=develop&label=Travis
    :target: https://travis-ci.org/malinoff/tatoo-cli

.. image:: https://ci.appveyor.com/api/projects/status/github/malinoff/tatoo-cli?svg=true&branch=develop&passingText=Appveyor%20|%20passing&pendingText=Appveyor%20|%20pending&failingText=Appveyor%20|%20failing
    :target: https://ci.appveyor.com/project/malinoff/tatoo-cli/branch/develop

Tatoo CLI
=========

Command-line interface for `tatoo <https://pypi.python.org/pypi/tatoo>`_
library.

Given the following ``tasks.py`` file::

    from tatoo import Environment, parameter
    from tatoo.tasks import types

    env = Environment('myenv')

    @env.task
    @parameter('x', type=types.Float)
    @parameter('y', type=types.Float)
    def add(x, y):
        print(x + y)

You can execute ``add`` task like this::

    $ tatoo -E tasks apply add 1 2
    3.0

It works under Python 2.6, 2.7, 3.3+ and Pypy (Pypy3 is not yet supported) on
Linux, OSX and Windows. This ensured on each commit continiously using
`TravisCI <https://travis-ci.org/malinoff/tatoo-cli/>`_ (Linux & OSX) and
`Appveyor <https://ci.appveyor.com/project/malinoff/tatoo-cli/>`_ (Windows).
