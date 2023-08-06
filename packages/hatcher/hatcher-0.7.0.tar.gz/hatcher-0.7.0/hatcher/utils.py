from contextlib import contextmanager

from click import Context, Group, option


class Indent(object):

    def __init__(self, width):
        self.width = width

    def __str__(self):
        return ' ' * self.width


class CommandTreeFormatter(object):
    """A helper to format the tree of click commands for printing on the
    console.

    """

    def __init__(self, indent_increment=4):
        self._buffer = []
        self._indent_increment = indent_increment
        self._current_indent = 0

    @contextmanager
    def indentation(self):
        """Context manager to control the indentation of the tree at the
        current command level.

        """
        self._current_indent += 1
        try:
            yield
        finally:
            self._current_indent -= 1
            assert self._current_indent >= 0

    def add_command(self, command):
        """Add a command to the tree at the current indentation level.

        """
        context = Context(command)
        if not isinstance(command, Group):
            usage = ' '.join(command.collect_usage_pieces(context))
        else:
            usage = ''
        buffered_output = (
            Indent(self._indent_increment * self._current_indent),
            command.name,
            usage,
        )
        self._buffer.append(buffered_output)

    def getvalue(self):
        """Return the formatted tree as a string.

        """
        max_width = max(len(str(indent)) + len(name)
                        for indent, name, usage in self._buffer)
        return '\n'.join(
            '{name: <{max_width}}   {usage}'.format(
                max_width=max_width,
                name='{}{}'.format(indent, name),
                usage=usage,
            )
            for indent, name, usage in self._buffer)

    def format(self, click_command):
        """Build the command tree starting from the provided ``click_command``.

        This is a recursive function that traverses the tree of click
        commands.

        """
        self.add_command(click_command)
        if isinstance(click_command, Group):
            with self.indentation():
                for name, next_command in sorted(
                        click_command.commands.items()):
                    self.format(next_command)


def _print_command_tree(click_command):
    formatter = CommandTreeFormatter()
    formatter.format(click_command)
    print(formatter.getvalue())


def print_command_tree(ctx, params, value):
    """ Print the full command tree starting from the context's command. """

    if value:
        _print_command_tree(ctx.command)
        ctx.exit()


def command_tree_option(*param_decls, **attrs):
    """ A decorator to add the command tree option.

    Adds an option `--command-tree` which prints the command tree for the
    given click command and exits.

    This is based on the click's `version_option` decorator.

    """

    def decorator(f):
        attrs.setdefault('is_flag', True)
        attrs.setdefault('expose_value', False)
        attrs.setdefault('is_eager', True)
        attrs.setdefault('help', 'Print the command tree and exit.')

        attrs['callback'] = print_command_tree

        return option(*(param_decls or ('--command-tree', )), **attrs)(f)

    return decorator
