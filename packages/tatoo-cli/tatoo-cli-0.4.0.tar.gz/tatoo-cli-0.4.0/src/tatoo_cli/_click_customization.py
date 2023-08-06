# -*- coding: utf-8 -*-
# Disable pylint, too many magic to deal with
# pylint: skip-file

import click
from click.utils import make_default_short_help
from click.formatting import join_options
from click.formatting import HelpFormatter
from click.formatting import wrap_text
from click.formatting import iter_rows
from click.formatting import measure_table
from click.formatting import term_len


# There are a lot of magic stuff here. This is because click is not very
# configurable, unfortunately, and it is covered in
# http://click.pocoo.org/3/why/#why-hardcoded-behaviors
#
# We create special TaskCommand class, yes, just to be able to modify
# the help output :(
# Click has no `short_help` for options and no `help` for arguments
# at all, so we define additional method `format_arguments` in
# our command class. Because of that we also implement
# custom Argument and Option classes.
#
# Also we create a special ManFormatter that echoes long
# help entries via $PAGER.

class TaskCommand(click.Command):
    """Special :class:`click.Command` subclass with revised help output."""

    def get_man(self, ctx):
        """Get man page."""
        formatter = ManFormatter(width=ctx.terminal_width)
        self.format_man(ctx, formatter)
        return formatter.getvalue().rstrip('\n')

    def format_man(self, ctx, formatter):
        """Writes the man page into the formatter if it exists."""
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter, short=False)
        self.format_arguments(ctx, formatter, short=False)
        self.format_options(ctx, formatter, short=False)
        self.format_epilog(ctx, formatter)

    def format_help(self, ctx, formatter):
        """Writes the help into the formatter if it exists.
        This calls into the following methods:
        - :meth:`format_usage`
        - :meth:`format_help_text`
        - :meth:`format_arguments`
        - :meth:`format_options`
        - :meth:`format_epilog`
        """
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_arguments(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def format_help_text(self, ctx, formatter, short=True):
        """Writes the short help text to the formatter if it exists."""
        # We don't need to put the long help here.
        help_ = self.short_help if short else self.help
        if help_:
            formatter.write_paragraph()
            with formatter.indentation():
                formatter.write_text(help_)

    def format_options(self, ctx, formatter, short=True):
        """Writes all the options into the formatter if they exist."""
        opts = []
        for param in self.get_params(ctx):
            try:
                rv = param.get_opt_help_record(ctx, short)
            except AttributeError:
                rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)

        if opts:
            with formatter.section('Options'):
                formatter.write_dl(opts)

    def format_arguments(self, ctx, formatter, short=True):
        """Writes all the options into the formatter if they exist."""
        args = []
        for param in self.get_params(ctx):
            try:
                record = param.get_arg_help_record(ctx, short)
            except AttributeError:
                continue
            if record is not None:
                args.append(record)

        if args:
            with formatter.section('Arguments'):
                formatter.write_dl(args)


class TaskOption(click.Option):  # pylint: disable=R0903
    """Special :class:`click.Option` subclass that adopts
    :ref:`click.Option` instances.
    """

    def __init__(self, param):
        self.param = param
        decls = (list(param.options) or []) + [param.dest]
        super(TaskOption, self).__init__(
            decls, type=param.type, required=param.required,
            default=param.default, metavar=param.metavar, envvar=param.envvar,
        )
        self.help = param.help if param.help is not None else ''
        self.short_help = param.short_help
        if self.short_help is None:
            self.short_help = make_default_short_help(self.help)

    def get_opt_help_record(self, ctx, short=True):
        any_prefix_is_slash = []

        def _write_opts(opts):  # pylint: disable=C0111
            record, any_slashes = join_options(opts)
            if any_slashes:
                any_prefix_is_slash[:] = [True]
            if not self.is_flag and not self.count:
                record += ' ' + self.make_metavar()
            return record

        record = [_write_opts(self.opts)]
        if self.secondary_opts:
            record.append(_write_opts(self.secondary_opts))

        help_ = self.short_help if short else self.help
        extra = []
        if self.default is not None and self.show_default:
            extra.append('default: %s' % self.default)
        if self.required:
            extra.append('required')
        if extra:
            help_ = '%s[%s]' % (help and help + '  ' or '', '; '.join(extra))

        return ((any_prefix_is_slash and '; ' or ' / ').join(record), help_)

    def get_arg_help_record(self, ctx, short):
        pass


class TaskArgument(click.Argument):  # pylint: disable=R0903
    """Special :class:`click.Argument` subclass that brings short and long
    help meanings to arguments.
    """

    def __init__(self, param):
        self.param = param
        super(TaskArgument, self).__init__(
            [param.dest], type=param.type, required=param.required,
            default=param.default, metavar=param.metavar, envvar=param.envvar,
        )
        self.default = param.default
        self.help = param.help if param.help is not None else ''
        self.short_help = param.short_help
        if self.short_help is None:
            self.short_help = make_default_short_help(self.help)

    def get_opt_help_record(self, ctx, short):
        pass

    def get_arg_help_record(self, ctx, short=True):  # pylint: disable=W0613
        """Returns the help record, if present."""
        help_ = self.short_help if short else self.help
        if help_:
            return (self.name, help_)


class ManFormatter(HelpFormatter):

    def write_dl(self, rows, col_max=30, col_spacing=2):
        """Writes a definition list into the buffer.  This is how options
        and commands are usually formatted.

        :param rows: a list of two item tuples for the terms and values.
        :param col_max: the maximum width of the first column.
        :param col_spacing: the number of spaces between the first and
                            second column.
        """
        rows = list(rows)
        widths = measure_table(rows)
        if len(widths) != 2:
            raise TypeError('Expected two columns for definition list')

        first_col = min(widths[0], col_max) + col_spacing

        for first, second in iter_rows(rows, len(widths)):
            self.write('\n%*s%s' % (self.current_indent, '', first))
            if not second:
                self.write('\n')
                continue
            if term_len(first) <= first_col - col_spacing:
                self.write(' ' * (first_col - term_len(first)))
            else:
                self.write('\n')
                self.write(' ' * (first_col + self.current_indent))

            text_width = max(self.width - first_col - 2, 10)
            lines = iter(wrap_text(second, text_width,
                                   preserve_paragraphs=True).splitlines())
            if lines:
                self.write(next(lines) + '\n')
                for line in lines:
                    self.write('%*s%s\n' % (
                        first_col + self.current_indent, '', line))
            else:
                self.write('\n')


def man_option(*param_decls, **attrs):
    """Adds a ``--man`` option which immediately ends the program
    printing out the help page. This is implemented as eager option that
    prints in the callback and exits.

    All arguments are forwarded to :func:`option`.
    """
    def decorator(fun):  # pylint: disable=C0111
        def callback(ctx, param, value):  # pylint: disable=C0111,W0613
            if value and not ctx.resilient_parsing:
                click.echo_via_pager(ctx.command.get_man(ctx))
                ctx.exit()
        attrs.setdefault('is_flag', True)
        attrs.setdefault('expose_value', False)
        attrs.setdefault('help', 'Open verbose help in a pager and exit.')
        attrs.setdefault('is_eager', True)
        attrs['callback'] = callback
        # pylint: disable=W0142
        return click.option(*(param_decls or ('--man',)), **attrs)(fun)
    return decorator
