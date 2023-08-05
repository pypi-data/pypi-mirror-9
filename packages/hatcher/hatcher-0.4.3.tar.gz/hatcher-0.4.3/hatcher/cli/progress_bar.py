import time

from click._termui_impl import ProgressBar


class ChunkProgressBar(ProgressBar):
    """A progress bar that determines its position based on the value of the
    generator.

    """

    def __init__(self, **kwargs):
        super(ChunkProgressBar, self).__init__(**kwargs)

    def make_step(self):
        self.pos += self.current_item
        if self.length_known and self.pos >= self.length:
            self.finished = True

        if (time.time() - self.last_eta) < 1.0:
            return

        self.last_eta = time.time()
        self.avg = self.avg[-6:] + [-(self.start - time.time()) / (self.pos)]

        self.eta_known = self.length_known


# Copied from click
def progressbar(iterable=None, length=None, label=None, show_eta=True,
                show_percent=None, show_pos=False,
                item_show_func=None, fill_char='#', empty_char='-',
                bar_template='%(label)s  [%(bar)s]  %(info)s',
                info_sep='  ', width=36, file=None, cls=ChunkProgressBar):
    """This function creates an iterable context manager that can be used
    to iterate over something while showing a progress bar.  It will
    either iterate over the `iterable` or `length` items (that are counted
    up).  While iteration happens, this function will print a rendered
    progress bar to the given `file` (defaults to stdout) and will attempt
    to calculate remaining time and more.  By default, this progress bar
    will not be rendered if the file is not a terminal.

    The context manager creates the progress bar.  When the context
    manager is entered the progress bar is already displayed.  With every
    iteration over the progress bar, the iterable passed to the bar is
    advanced and the bar is updated.  When the context manager exits,
    a newline is printed and the progress bar is finalized on screen.

    No printing must happen or the progress bar will be unintentionally
    destroyed.

    Example usage::

        with progressbar(items) as bar:
            for item in bar:
                do_something_with(item)

    .. versionadded:: 2.0

    :param iterable: an iterable to iterate over.  If not provided the length
                     is required.
    :param length: the number of items to iterate over.  By default the
                   progressbar will attempt to ask the iterator about its
                   length, which might or might not work.  If an iterable is
                   also provided this parameter can be used to override the
                   length.  If an iterable is not provided the progress bar
                   will iterate over a range of that length.
    :param label: the label to show next to the progress bar.
    :param show_eta: enables or disables the estimated time display.  This is
                     automatically disabled if the length cannot be
                     determined.
    :param show_percent: enables or disables the percentage display.  The
                         default is `True` if the iterable has a length or
                         `False` if not.
    :param show_pos: enables or disables the absolute position display.  The
                     default is `False`.
    :param item_show_func: a function called with the current item which
                           can return a string to show the current item
                           next to the progress bar.  Note that the current
                           item can be `None`!
    :param fill_char: the character to use to show the filled part of the
                      progress bar.
    :param empty_char: the character to use to show the non-filled part of
                       the progress bar.
    :param bar_template: the format string to use as template for the bar.
                         The parameters in it are ``label`` for the label,
                         ``bar`` for the progress bar and ``info`` for the
                         info section.
    :param info_sep: the separator between multiple info items (eta etc.)
    :param width: the width of the progress bar in characters, 0 means full
                  terminal width
    :param file: the file to write to.  If this is not a terminal then
                 only the label is printed.
    """
    return cls(iterable=iterable, length=length, show_eta=show_eta,
               show_percent=show_percent, show_pos=show_pos,
               item_show_func=item_show_func, fill_char=fill_char,
               empty_char=empty_char, bar_template=bar_template,
               info_sep=info_sep, file=file, label=label,
               width=width)
