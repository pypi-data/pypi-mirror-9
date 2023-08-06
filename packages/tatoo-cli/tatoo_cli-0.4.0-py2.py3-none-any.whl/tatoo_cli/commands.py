# -*- coding: utf-8 -*-
"""

    tatoo_cli.commands
    ~~~~~~~~~~~~~~~~~~

    All commands that tatoo-cli defines.

"""

from __future__ import absolute_import, unicode_literals, print_function

from types import ModuleType

from six import itervalues, string_types

import click

from tatoo.task import types

from tatoo.log import LOG_LEVELS
from tatoo.interfaces import IEnvironment
from tatoo.environment import Environment
from tatoo.utils.imports import symbol_by_name, import_from_cwd as imp

from tatoo_cli import __version__
from tatoo_cli.tasks import Tasks
from tatoo_cli.signals import register_subcommands

LOG_LEVEL_CHOICES = [l for l in LOG_LEVELS if isinstance(l, string_types)]

# Monkey patch click.types.convert_type - it's hardcoded in
# click.core.Parameter's constructor :(
click.core.convert_type = types._convert_type


def find_env(env, importer=imp):
    """Given a string like "package.module.submodule:object" this
    resolves it, imports all modules and returns ``object``.

    If no ``object`` is specified, it will try to find an instance
    of :ref:`tatoo.environment.Environment` class.

    If an object is passed instead of string, it is returned immediately.
    """
    if env is None:
        return Environment('default')
    try:
        sym = symbol_by_name(env, imp=importer)
    except AttributeError:
        # Last part was not an attribute, but a module
        sym = importer(env)
    if isinstance(sym, ModuleType):
        try:
            found = sym.env
            if isinstance(found, ModuleType):
                raise TypeError
        except AttributeError:
            for suspect in itervalues(vars(sym)):
                if IEnvironment.providedBy(suspect):
                    return suspect
            raise
        return found
    return sym


class UmbrellaGroup(click.Group):

    def __init__(self, *args, **kwargs):
        super(UmbrellaGroup, self).__init__(*args, **kwargs)
        register_subcommands.send(sender=self)


@click.command(cls=UmbrellaGroup)
@click.option('--env', '-E', metavar='ENV',
              help='Custom environment.')
@click.option('--loglevel', '-l', metavar='LEVEL',
              type=types.CaseInsensitiveChoice(LOG_LEVEL_CHOICES),
              help='Logging level.', default=None)
@click.option('--logfile', '-f', metavar='FILE',
              type=types.Path(dir_okay=False, writable=True,
                              resolve_path=True),
              help='Path to the logfile. If not specified, stderr is used',
              default=None)
@click.option('--outputter', help='Custom result outputter.',
              type=types.String, default=None)
@click.version_option(__version__, '-V', '--version')
@click.pass_context
def umbrella(ctx, env, loglevel, logfile, outputter):
    """tatoo - task toolkit."""
    env = ctx.obj = find_env(env)
    if loglevel is not None:
        env.settings['TATOO_LOG_LEVEL'] = loglevel
    if logfile is not None:
        env.settings['TATOO_LOG_FILE'] = logfile
    if outputter is not None:
        env.settings['CLI_OUTPUTTER'] = outputter
    env.logger.setup()
    env.extensions.load_from_entry_points()


@umbrella.command()
@click.pass_obj
def bugreport(env):
    """Shows information useful in bugreports."""
    print(env.bugreport())


@umbrella.command(cls=Tasks, subcommand_metavar='TASK [ARGS]...')
@click.option('--no-propagate', required=False, is_flag=True, default=True,
              help='If specified, any exception occurred during execution '
                   'will not be propagated.')
@click.option('--request-id', required=False, help='Custom request id.',
              type=types.String, default=None)
@click.pass_context
def apply(ctx, no_propagate, request_id):
    """Apply a task locally."""
    ctx.propagate = no_propagate
    ctx.request_id = request_id
