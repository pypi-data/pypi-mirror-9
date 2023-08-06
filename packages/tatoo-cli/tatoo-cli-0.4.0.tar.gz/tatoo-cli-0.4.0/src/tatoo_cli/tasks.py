# -*- coding: utf-8 -*-
"""

    tatoo_cli.tasks
    ~~~~~~~~~~~~~~~

    Utilities to handle tasks invocations.

"""

from __future__ import absolute_import, unicode_literals, print_function

from click import Group
from click import pass_context

from tatoo_cli.interfaces import IOutputter
from tatoo_cli._click_customization import man_option
from tatoo_cli._click_customization import TaskOption
from tatoo_cli._click_customization import TaskCommand
from tatoo_cli._click_customization import TaskArgument


def _argument_or_option(param):  # pylint: disable=C0111
    if not param.options:
        return TaskArgument(param)
    return TaskOption(param)


class Tasks(Group):
    """Dynamically load available tasks."""

    def list_commands(self, ctx):
        return sorted(list(ctx.obj.tasks))

    def get_command(self, ctx, name):
        task = ctx.obj.tasks[name]
        # Convert instances of tatoo.task.Parameter to
        # click.Argument and click.Option instances.
        params = [_argument_or_option(param) for param in task.parameters]
        placeholder = task_placeholder
        placeholder.__click_params__ = params
        placeholder.__doc__ = task.__doc__
        pass_context(placeholder)
        man_option()(placeholder)
        return ctx.command.command(name=name, cls=TaskCommand)(placeholder)

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        rows = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command. Ignore it
            if cmd is None:  # pragma: no cover
                continue
            help_ = cmd.short_help or cmd.help or ''
            rows.append((subcommand, help_))
        if not rows:
            with formatter.section('Tasks'):
                formatter.write('  No registered tasks')
        else:
            with formatter.section('Tasks'):
                formatter.write_dl(rows)


def task_placeholder(ctx, *args, **kwargs):  # pylint: disable=C0111
    # Placeholder for a task command, will be decorated using
    # click.command(), see Tasks.get_command
    name = ctx.info_name
    env = ctx.obj
    ctx = ctx.parent
    request_id = getattr(ctx, 'request_id', None)
    res = env.tasks[name].apply(
        request_id=request_id, args=args, kwargs=kwargs,
    )
    if getattr(ctx, 'propagate', True):
        # Fail fast
        res.get(propagate=True)
    outputter = getattr(ctx, 'outputter', env.settings.CLI_OUTPUTTER)
    if outputter is not None:
        outputter = env.getUtility(IOutputter, outputter)
        print(outputter.format(res))
    return res
