from __future__ import unicode_literals
from pygments.formatters.terminal256 import Terminal256Formatter, EscapeSequence

from prompt_toolkit.layout.screen import Size

import array
import fcntl
import six
import termios
import errno


# Global variable to keep the colour table in memory.
_tf = Terminal256Formatter()

#: If True: write the output of the renderer also to the following file. This
#: is very useful for debugging. (e.g.: to see that we don't write more bytes
#: than required.)
_DEBUG_RENDER_OUTPUT = False
_DEBUG_RENDER_OUTPUT_FILENAME = '/tmp/prompt-toolkit-render-output'


def _get_size(fileno):
    # Thanks to fabric (fabfile.org), and
    # http://sqizit.bartletts.id.au/2011/02/14/pseudo-terminals-in-python/
    """
    Get the size of this pseudo terminal.

    :param fileno: stdout.fileno()
    :returns: A (rows, cols) tuple.
    """
#    assert stdout.isatty()

    # Buffer for the C call
    buf = array.array(u'h' if six.PY3 else b'h', [0, 0, 0, 0])

    # Do TIOCGWINSZ (Get)
    fcntl.ioctl(fileno, termios.TIOCGWINSZ, buf, True)

    # Return rows, cols
    return buf[0], buf[1]


class Vt100_Output(object):
    def __init__(self, stdout):
        self._buffer = []
        self.stdout = stdout

    def get_size(self):
        rows, columns = _get_size(self.stdout.fileno())
        return Size(rows=rows, columns=columns)

    def write(self, data):
        self._buffer.append(data)

    def erase_screen(self):
        """
        Erases the screen with the background colour and moves the cursor to
        home.
        """
        self.write('\x1b[2J')

    def enter_alternate_screen(self):
        self.write('\x1b[?1049h\x1b[H')

    def quit_alternate_screen(self):
        self.write('\x1b[?1049l')

    def erase_end_of_line(self):
        """
        Erases from the current cursor position to the end of the current line.
        """
        self.write('\x1b[K')

    def erase_down(self):
        """
        Erases the screen from the current line down to the bottom of the
        screen.
        """
        self.write('\x1b[J')

    def newline(self):
        self.write('\n')

    def carriage_return(self):
        self.write('\r')

    def reset_attributes(self):
        self.write('\x1b[0m')

    def set_attributes(self, fgcolor=None, bgcolor=None, bold=False, underline=False):
        """
        Create new style and output.
        """
        fg = _tf._color_index(fgcolor) if fgcolor else None
        bg = _tf._color_index(bgcolor) if bgcolor else None

        e = EscapeSequence(fg=fg, bg=bg, bold=bold, underline=underline)

        self.reset_attributes()
        self.write(e.color_string())

    def disable_autowrap(self):
        self.write('\x1b[?7l')

    def enable_autowrap(self):
        self.write('\x1b[?7h')

    def cursor_goto(self, row=0, column=0):
        """ Move cursor position. """
        self.write('\x1b[%i;%iH' % (row, column))

    def cursor_up(self, amount):
        if amount == 0:
            self.write('')
        elif amount == 1:
            self.write('\x1b[A')
        else:
            self.write('\x1b[%iA' % amount)

    def cursor_down(self, amount):
        if amount == 0:
            self.write('')
        elif amount == 1:
            # Note: Not the same as '\n', '\n' can cause the window content to
            #       scroll.
            self.write('\x1b[B')
        else:
            self.write('\x1b[%iB' % amount)

    def cursor_forward(self, amount):
        if amount == 0:
            self.write('')
        elif amount == 1:
            self.write('\x1b[C')
        else:
            self.write('\x1b[%iC' % amount)

    def cursor_backward(self, amount):
        if amount == 0:
            self.write('')
        elif amount == 1:
            self.write('\b')  # '\x1b[D'
        else:
            self.write('\x1b[%iD' % amount)

    def flush(self):
        """
        Write to output stream and flush.
        """
        if not self._buffer:
            return

        data = ''.join(self._buffer)

        try:
            self.stdout.write(data)
            self.stdout.flush()
        except IOError as e:
            if e.args and e.args[0] == errno.EINTR:
                # Interrupted system call. Can happpen in case of a window
                # resize signal. (Just ignore. The resize handler will render
                # again anyway.)
                pass
            else:
                raise

        self._buffer = []
