"""
Renders the command line on the console.
(Redraws parts of the input line that were changed.)
"""
from __future__ import unicode_literals
import sys
import errno

from pygments.style import Style
from pygments.token import Token
from prompt_toolkit.layout.screen import Point, Screen, Char, WritePosition

if sys.platform == 'win32':
    from .terminal.win32_output import Win32Output as Output
else:
    from .terminal.vt100_output import Vt100_Output as Output

__all__ = (
    'Renderer',
)


def output_screen_diff(output, screen, current_pos, previous_screen=None, last_char=None,
                       is_done=False, style=None, grayed=False):  # XXX: drop is_done and grayed!!
    """
    Create diff of this screen with the previous screen.
    """
    #: Remember the last printed character.
    last_char = [last_char]  # nonlocal
    background_turned_on = [False]  # Nonlocal

    #: Variable for capturing the output.
    write = output.write

    def move_cursor(new):
        current_x, current_y = current_pos.x, current_pos.y

        if new.y > current_y:
            # Use newlines instead of CURSOR_DOWN, because this meight add new lines.
            # CURSOR_DOWN will never create new lines at the bottom.
            # Also reset attributes, otherwise the newline could draw a
            # background color.
            output.reset_attributes()
            write('\r\n' * (new.y - current_y))
            current_x = 0
            output.cursor_forward(new.x)
            last_char[0] = None  # Forget last char after resetting attributes.
            return new
        elif new.y < current_y:
            output.cursor_up(current_y - new.y)

        if current_x >= screen.width - 1:
            write('\r')
            output.cursor_forward(new.x)
        elif new.x < current_x or current_x >= screen.width - 1:
            output.cursor_backward(current_x - new.x)
        elif new.x > current_x:
            output.cursor_forward(new.x - current_x)

        return new

    def get_style_for_token(token):
        """
        Get style
        """
        # If grayed, replace token
        if grayed:
            token = Token.Aborted

        try:
            return style.style_for_token(token)
        except KeyError:
            return None

    def chars_are_equal(new_char, old_char):
        """
        Test whether two `Char` instances are equal if printed.
        """
        if grayed:
            new_char = Char(new_char.char, token=Token.Aborted)

        # We ignore z-index, that does not matter if things get painted.
        return new_char.char == old_char.char and new_char.token == old_char.token

    def output_char(char):
        """
        Write the output of this charact.r
        """
        # If the last printed character has the same token, it also has the
        # same style, so we don't output it.
        if last_char[0] and last_char[0].token == char.token:
            write(char.char)
        else:
            style = get_style_for_token(char.token)

            if style:
                output.set_attributes(style['color'], style['bgcolor'],
                                      bold=style.get('bold', False),
                                      underline=style.get('underline', False))

                # If we print something with a background color, remember that.
                background_turned_on[0] = bool(style['bgcolor'])
            else:
                # Reset previous style and output.
                output.reset_attributes()

            write(char.char)

        last_char[0] = char

    # Disable autowrap
    if not previous_screen:
        output.disable_autowrap()
        output.reset_attributes()

    # When the previous screen has a different size, redraw everything anyway.
    # Also when we are done. (We meight take up less rows, so clearing is important.)
    if is_done or not previous_screen or previous_screen.width != screen.width:  # XXX: also consider height??
        current_pos = move_cursor(Point(0, 0))
        output.reset_attributes()
        output.erase_down()

        previous_screen = Screen(screen.width)

    # Get height of the screen.
    # (current_height changes as we loop over _buffer, so remember the current value.)
    current_height = screen.current_height

    # Loop over the rows.
    row_count = max(screen.current_height, previous_screen.current_height)
    c = 0  # Column counter.

    for y, r in enumerate(range(0, row_count)):
        new_row = screen._buffer[r]
        previous_row = previous_screen._buffer[r]

        new_max_line_len = max(new_row.keys()) if new_row else 0
        previous_max_line_len = max(previous_row.keys()) if previous_row else 0

        # Loop over the columns.
        c = 0
        while c < new_max_line_len + 1:
            char_width = (new_row[c].width or 1)

            if not chars_are_equal(new_row[c], previous_row[c]):
                current_pos = move_cursor(Point(y=y, x=c))
                output_char(new_row[c])
                current_pos = current_pos._replace(x=current_pos.x + char_width)

            c += char_width

        # If the new line is shorter, trim it
        if previous_screen and new_max_line_len < previous_max_line_len:
            current_pos = move_cursor(Point(y=y, x=new_max_line_len+1))
            output.reset_attributes()
            output.erase_end_of_line()
            last_char[0] = None  # Forget last char after resetting attributes.

    # Move cursor:
    if is_done:
        current_pos = move_cursor(Point(y=current_height, x=0))
        output.erase_down()
    else:
        current_pos = move_cursor(screen.cursor_position)

    if is_done:
        output.reset_attributes()
        output.enable_autowrap()

    # If the last printed character has a background color, always reset.
    # (Many terminals give weird artifacs on resize events when there is an
    # active background color.)
    if background_turned_on[0]:
        output.reset_attributes()
        last_char[0] = None

    return current_pos, last_char[0]


class Renderer(object):
    """
    Typical usage:

    ::

        r = Renderer(sys.stdout)
        r.render(cli, layout=..., style=...)
    """
    def __init__(self, stdout=None, use_alternate_screen=False):  # XXX: implement alternate screen for Windows.
        self.stdout = stdout or sys.stdout
        self.use_alternate_screen = use_alternate_screen

        self._in_alternate_screen = False

        self.output = Output(self.stdout)

        self.reset()

    def reset(self):
        # Reset position
        self._cursor_pos = Point(x=0, y=0)

        # Remember the last screen instance between renderers. This way,
        # we can create a `diff` between two screens and only output the
        # difference. It's also to remember the last height. (To show for
        # instance a toolbar at the bottom position.)
        self._last_screen = None
        self._last_size = None
        self._last_char = None

        #: Space from the top of the layout, until the bottom of the terminal.
        #: We don't know this until a `report_absolute_cursor_row` call.
        self._min_available_height = 0

        # In case of Windown, also make sure to scroll to the current cursor
        # position.
        if sys.platform == 'win32':
            self.output.scroll_buffer_to_prompt()

        # Quit alternate screen.
        if self._in_alternate_screen:
            self.output.quit_alternate_screen()
            self.output.flush()
            self._in_alternate_screen = False

    @property
    def height_is_known(self):
        """
        True when the height from the cursor until the bottom of the terminal
        is known. (It's often nicer to draw bottom toolbars only if the height
        is known, in order to avoid flickering when the CPR response arrives.)
        """
        return self.use_alternate_screen or self._min_available_height > 0 or \
            sys.platform == 'win32'  # On Windows, we don't have to wait for a CPR.

    def _write_and_flush(self, data):
        """
        Write to output stream and flush.
        """
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

    def request_absolute_cursor_position(self):
        """
        Get current cursor position.
        For vt100: Do CPR request. (answer will arrive later.)
        For win32: Do API call. (Answer comes immediately.)
        """
        # Only do this request when the cursor is at the top row. (after a
        # clear or reset). We will rely on that in `report_absolute_cursor_row`.
        assert self._cursor_pos.y == 0

        # For Win32, we have an API call to get the number of rows below the
        # cursor.
        if sys.platform == 'win32':
            self._min_available_height = self.output.get_rows_below_cursor_position()
        else:
            if self.use_alternate_screen:
                self._min_available_height = self.output.get_size().rows
            else:
                # Asks for a cursor position report (CPR).
                self._write_and_flush('\x1b[6n')

    def report_absolute_cursor_row(self, row):
        """
        To be called when we know the absolute cursor position.
        (As an answer of a "Cursor Position Request" response.)
        """
        # Calculate the amount of rows from the cursor position until the
        # bottom of the terminal.
        total_rows = self.output.get_size().rows
        rows_below_cursor = total_rows - row + 1

        # Set the
        self._min_available_height = rows_below_cursor

    def render(self, cli, layout, style=None):
        """
        Render the current interface to the output.
        """
        style = style or Style
        output = self.output

        # Enter alternate screen.
        if self.use_alternate_screen and not self._in_alternate_screen:
            self._in_alternate_screen = True
            output.enter_alternate_screen()

        # Create screen and write layout to it.
        size = output.get_size()
        screen = Screen(size.columns)

        if cli.is_done:
            height = 0  # When we are done, we don't necessary want to fill up until the bottom.
        else:
            height = self._last_screen.current_height if self._last_screen else 0
            height = max(self._min_available_height, height)

        # When te size changes, don't consider the previous screen.
        if self._last_size != size:
            self._last_screen=None

        layout.write_to_screen(cli, screen, WritePosition(
            xpos=0,
            ypos=0,
            width=size.columns,
            height=(size.rows if self.use_alternate_screen else height),
            extended_height=size.rows,
        ))

        # Process diff and write to output.
        self._cursor_pos, self._last_char = output_screen_diff(
            output, screen, self._cursor_pos,
            self._last_screen, self._last_char, cli.is_done,
            style=style, grayed=(cli.is_aborting or cli.is_exiting),
            )
        self._last_screen = screen
        self._last_size = size

        output.flush()

    def erase(self):
        """
        Hide all output and put the cursor back at the first line. This is for
        instance used for running a system command (while hiding the CLI) and
        later resuming the same CLI.)
        """
        output = self.output

        output.cursor_backward(self._cursor_pos.x)
        output.cursor_up(self._cursor_pos.y)
        output.erase_down()
        output.reset_attributes()
        output.flush()

        self.reset()

    def clear(self):
        """
        Clear screen and go to 0,0
        """
        # Erase current output first.
        self.erase()

        # Send "Erase Screen" command and go to (0, 0).
        output = self.output

        output.erase_screen()
        output.cursor_goto(0, 0)
        output.flush()

        self.request_absolute_cursor_position()
