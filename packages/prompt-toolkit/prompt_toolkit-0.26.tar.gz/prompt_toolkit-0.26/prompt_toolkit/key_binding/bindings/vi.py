from __future__ import unicode_literals
from prompt_toolkit.enums import IncrementalSearchDirection
from prompt_toolkit.keys import Keys
from prompt_toolkit.buffer import ClipboardData, indent, unindent
from prompt_toolkit.selection import SelectionType
from prompt_toolkit.key_binding.vi_state import ViState, CharacterFind, InputMode
from prompt_toolkit.filters import Filter

from .basic import load_basic_bindings
from .utils import create_handle_decorator

import prompt_toolkit.filters as filters
import codecs

__all__ = (
    'load_vi_bindings',
    'load_vi_search_bindings',
    'load_vi_system_bindings',
)


class ViStateFilter(Filter):
    """
    Filter to enable some key bindings only in a certain Vi input mode.
    """
    def __init__(self, vi_state, mode):
        self.vi_state = vi_state
        self.mode = mode

    def __call__(self, cli):
        return self.vi_state.input_mode == self.mode


class CursorRegion(object):
    """
    Return struct for functions wrapped in ``change_delete_move_yank_handler``.
    """
    def __init__(self, start, end=0):
        self.start = start
        self.end = end

    def sorted(self):
        """
        Return a (start, end) tuple where start <= end.
        """
        if self.start < self.end:
            return self.start, self.end
        else:
            return self.end, self.start


def load_vi_bindings(registry, vi_state, filter=None):
    """
    Vi extensions.

    # Overview of Readline Vi commands:
    # http://www.catonmat.net/download/bash-vi-editing-mode-cheat-sheet.pdf
    """
    assert isinstance(vi_state, ViState)

    load_basic_bindings(registry, filter)
    handle = create_handle_decorator(registry, filter)

    insert_mode = ViStateFilter(vi_state, InputMode.INSERT) & ~ filters.HasSelection()
    navigation_mode = ViStateFilter(vi_state, InputMode.NAVIGATION) & ~ filters.HasSelection()
    replace_mode = ViStateFilter(vi_state, InputMode.REPLACE) & ~ filters.HasSelection()
    selection_mode = filters.HasSelection()

    vi_transform_functions = [
        # Rot 13 transformation
        (('g', '?'), lambda string: codecs.encode(string, 'rot_13')),

        # To lowercase
        (('g', 'u'), lambda string: string.lower()),

        # To uppercase.
        (('g', 'U'), lambda string: string.upper()),

        # Swap case.
        # (XXX: If we would implement 'tildeop', the 'g' prefix is not required.)
        (('g', '~'), lambda string: string.swapcase()),
    ]

    def check_cursor_position(event):
        """
        After every command, make sure that if we are in navigation mode, we
        never put the cursor after the last character of a line. (Unless it's
        an empty line.)
        """
        buffer = event.current_buffer

        if (
                (filter is None or filter(event.cli)) and  # First make sure that this key bindings are active.

                vi_state.input_mode == InputMode.NAVIGATION and
                buffer.document.is_cursor_at_the_end_of_line and
                len(buffer.document.current_line) > 0):
            buffer.cursor_position -= 1

    registry.onHandlerCalled += check_cursor_position

    @handle(Keys.Escape)
    def _(event):
        """
        Escape goes to vi navigation mode.
        """
        buffer = event.current_buffer

        if vi_state.input_mode in (InputMode.INSERT, InputMode.REPLACE):
            buffer.cursor_position += buffer.document.get_cursor_left_position()

        vi_state.input_mode = InputMode.NAVIGATION

        if bool(buffer.selection_state):
            buffer.exit_selection()

    @handle('k', filter=navigation_mode)
    def _(event):
        """
        Arrow up in navigation mode.
        """
        event.current_buffer.auto_up(count=event.arg)

    @handle('j', filter=navigation_mode)
    def _(event):
        """
        Arrow down in navigation mode.
        """
        event.current_buffer.auto_down(count=event.arg)

    @handle('k', filter=selection_mode)
    def _(event):
        """
        Arrow up in selection mode.
        """
        event.current_buffer.cursor_up(count=event.arg)

    @handle('j', filter=selection_mode)
    def _(event):
        """
        Arrow down in selection mode.
        """
        event.current_buffer.cursor_down(count=event.arg)

    @handle(Keys.Up, filter=navigation_mode)
    def _(event):
        """
        Arrow up in navigation mode.
        """
        event.current_buffer.auto_up(count=event.arg)

    @handle(Keys.Down, filter=navigation_mode)
    def _(event):
        """
        Arrow down in navigation mode.
        """
        event.current_buffer.auto_down(count=event.arg)

    @handle(Keys.Backspace, filter=navigation_mode)
    def _(event):
        """
        In navigation-mode, move cursor.
        """
        event.current_buffer.cursor_position += \
            event.current_buffer.document.get_cursor_left_position(count=event.arg)

    @handle(Keys.ControlV, Keys.Any, filter=insert_mode)
    def _(event):
        """
        Insert a character literally (quoted insert).
        """
        event.current_buffer.insert_text(event.data, overwrite=False)

    @handle(Keys.ControlN, filter=insert_mode)
    def _(event):
        event.current_buffer.complete_next()

    @handle(Keys.ControlN, filter=navigation_mode)
    def _(event):
        """
        Control-N: Next completion.
        """
        event.current_buffer.auto_down()

    @handle(Keys.ControlP, filter=insert_mode)
    def _(event):
        """
        Control-P: To previous completion.
        """
        event.current_buffer.complete_previous()

    @handle(Keys.ControlY, filter=insert_mode)
    def _(event):
        """
        Accept current completion.
        """
        event.current_buffer.complete_state = None

    @handle(Keys.ControlE, filter=insert_mode)
    def _(event):
        """
        Cancel completion. Go back to originally typed text.
        """
        event.current_buffer.cancel_completion()

    @handle(Keys.ControlP, filter=navigation_mode)
    def _(event):
        """
        CtrlP in navigation mode goes up.
        """
        event.current_buffer.auto_up()

    @handle(Keys.ControlJ, filter=navigation_mode)
    def _(event):
        """
        In navigation mode, pressing enter will always return the input.
        """
        if event.current_buffer.validate():
            event.current_buffer.add_to_history()
            event.cli.set_return_value(event.current_buffer.document)

    # ** In navigation mode **

    # List of navigation commands: http://hea-www.harvard.edu/~fine/Tech/vi.html

    @handle('a', filter=navigation_mode)
    def _(event):
        event.current_buffer.cursor_position += event.current_buffer.document.get_cursor_right_position()
        vi_state.input_mode = InputMode.INSERT

    @handle('A', filter=navigation_mode)
    def _(event):
        event.current_buffer.cursor_position += event.current_buffer.document.get_end_of_line_position()
        vi_state.input_mode = InputMode.INSERT

    @handle('C', filter=navigation_mode)
    def _(event):
        """
        # Change to end of line.
        # Same as 'c$' (which is implemented elsewhere.)
        """
        buffer = event.current_buffer

        deleted = buffer.delete(count=buffer.document.get_end_of_line_position())
        event.cli.clipboard.set_text(deleted)
        vi_state.input_mode = InputMode.INSERT

    @handle('c', 'c', filter=navigation_mode)
    @handle('S', filter=navigation_mode)
    def _(event):  # TODO: implement 'arg'
        """
        Change current line
        """
        buffer = event.current_buffer

        # We copy the whole line.
        data = ClipboardData(buffer.document.current_line, SelectionType.LINES)
        event.cli.clipboard.set_data(data)

        # But we delete after the whitespace
        buffer.cursor_position += buffer.document.get_start_of_line_position(after_whitespace=True)
        buffer.delete(count=buffer.document.get_end_of_line_position())
        vi_state.input_mode = InputMode.INSERT

    @handle('D', filter=navigation_mode)
    def _(event):
        buffer = event.current_buffer
        deleted = buffer.delete(count=buffer.document.get_end_of_line_position())
        event.cli.clipboard.set_text(deleted)

    @handle('d', 'd', filter=navigation_mode)
    def _(event):
        """
        Delete line. (Or the following 'n' lines.)
        """
        buffer = event.current_buffer

        # Split string in before/deleted/after text.
        lines = buffer.document.lines

        before = '\n'.join(lines[:buffer.document.cursor_position_row])
        deleted = '\n'.join(lines[buffer.document.cursor_position_row: buffer.document.cursor_position_row + event.arg])
        after = '\n'.join(lines[buffer.document.cursor_position_row + event.arg:])

        # Set new text.
        if before and after:
            before = before + '\n'

        buffer.text = before + after

        # Set cursor position. (At the start of the first 'after' line, after the leading whitespace.)
        buffer.cursor_position = len(before) + len(after) - len(after.lstrip(' '))

        # Set clipboard data
        event.cli.clipboard.set_data(ClipboardData(deleted, SelectionType.LINES))

    @handle('G', filter=navigation_mode)
    def _(event):
        """
        If an argument is given, move to this line in the  history. (for
        example, 15G) Otherwise, go the the last line of the current string.
        """
        buffer = event.current_buffer

        # If an arg has been given explicitely.
        if event._arg:
            buffer.go_to_history(event.arg - 1)

        # Otherwise this goes to the last line of the file.
        else:
            buffer.cursor_position = len(buffer.text)

    @handle('i', filter=navigation_mode)
    def _(event):
        vi_state.input_mode = InputMode.INSERT

    @handle('I', filter=navigation_mode)
    def _(event):
        vi_state.input_mode = InputMode.INSERT
        event.current_buffer.cursor_position += event.current_buffer.document.get_start_of_line_position(after_whitespace=True)

    @handle('J', filter=navigation_mode)
    def _(event):
        for i in range(event.arg):
            event.current_buffer.join_next_line()

    @handle('n', filter=navigation_mode)
    def _(event):  # XXX: use `change_delete_move_yank_handler` and implement 'arg'
        """
        Search next.
        """
        event.current_buffer.incremental_search(vi_state.search_direction)

    @handle('N', filter=navigation_mode)
    def _(event):  # TODO: use `change_delete_move_yank_handler` and implement 'arg'
        """
        Search previous.
        """
        if vi_state.search_direction == IncrementalSearchDirection.BACKWARD:
            event.current_buffer.incremental_search(IncrementalSearchDirection.FORWARD)
        else:
            event.current_buffer.incremental_search(IncrementalSearchDirection.BACKWARD)

    @handle('p', filter=navigation_mode)
    def _(event):
        """
        Paste after
        """
        event.current_buffer.paste_clipboard_data(
            event.cli.clipboard.get_data(),
            count=event.arg)

    @handle('P', filter=navigation_mode)
    def _(event):
        """
        Paste before
        """
        event.current_buffer.paste_clipboard_data(
            event.cli.clipboard.get_data(),
            before=True,
            count=event.arg)

    @handle('r', Keys.Any, filter=navigation_mode)
    def _(event):
        """
        Replace single character under cursor
        """
        event.current_buffer.insert_text(event.data * event.arg, overwrite=True)
        event.current_buffer.cursor_position -= 1

    @handle('R', filter=navigation_mode)
    def _(event):
        """
        Go to 'replace'-mode.
        """
        vi_state.input_mode = InputMode.REPLACE

    @handle('s', filter=navigation_mode)
    def _(event):
        """
        Substitute with new text
        (Delete character(s) and go to insert mode.)
        """
        text = event.current_buffer.delete(count=event.arg)
        event.cli.clipboard.set_text(text)
        vi_state.input_mode = InputMode.INSERT

    @handle('u', filter=navigation_mode)
    def _(event):
        for i in range(event.arg):
            event.current_buffer.undo()

    @handle('v', filter=navigation_mode)
    def _(event):
        event.current_buffer.open_in_editor()

    # @handle('v', filter=navigation_mode)
    # def _(event):
    #     """
    #     Start characters selection.
    #     """
    #     event.current_buffer.start_selection(selection_type=SelectionType.CHARACTERS)

    @handle('V', filter=navigation_mode)
    def _(event):
        """
        Start lines selection.
        """
        event.current_buffer.start_selection(selection_type=SelectionType.LINES)

    @handle('a', 'w', filter=selection_mode)
    @handle('a', 'W', filter=selection_mode)
    def _(event):
        """
        Switch from visual linewise mode to visual characterwise mode.
        """
        buffer = event.current_buffer

        if buffer.selection_state and buffer.selection_state.type == SelectionType.LINES:
            buffer.selection_state.type = SelectionType.CHARACTERS

    @handle('x', filter=navigation_mode)
    def _(event):
        """
        Delete character.
        """
        text = event.current_buffer.delete(count=event.arg)
        event.cli.clipboard.set_text(text)

    @handle('x', filter=selection_mode)
    @handle('d', 'd', filter=selection_mode)
    def _(event):
        """
        Cut selection.
        """
        clipboard_data = event.current_buffer.cut_selection()
        event.cli.clipboard.set_data(clipboard_data)

    @handle('c', filter=selection_mode)
    def _(event):
        """
        Change selection (cut and go to insert mode).
        """
        buffer = event.current_buffer

        selection_type = buffer.selection_state.type
        deleted = buffer.cut_selection()
        event.cli.clipboard.set_data(ClipboardData(deleted, selection_type))
        vi_state.input_mode = InputMode.INSERT

    @handle('y', filter=selection_mode)
    def _(event):
        """
        Copy selection.
        """
        clipboard_data = event.current_buffer.copy_selection()
        event.cli.clipboard.set_data(clipboard_data)

    @handle('X', filter=navigation_mode)
    def _(event):
        text = event.current_buffer.delete_before_cursor()
        event.cli.clipboard.set_text(text)

    @handle('y', 'y', filter=navigation_mode)
    @handle('Y', filter=navigation_mode)
    def _(event):
        """
        Yank the whole line.
        """
        text = '\n'.join(event.current_buffer.document.lines_from_current[:event.arg])
        event.cli.clipboard.set_data(ClipboardData(text, SelectionType.LINES))

    @handle('+', filter=navigation_mode)
    def _(event):
        """
        Move to first non whitespace of next line
        """
        buffer = event.current_buffer
        buffer.cursor_position += buffer.document.get_cursor_down_position(count=event.arg)
        buffer.cursor_position += buffer.document.get_start_of_line_position(after_whitespace=True)

    @handle('-', filter=navigation_mode)
    def _(event):
        """
        Move to first non whitespace of previous line
        """
        buffer = event.current_buffer
        buffer.cursor_position += buffer.document.get_cursor_up_position(count=event.arg)
        buffer.cursor_position += buffer.document.get_start_of_line_position(after_whitespace=True)

    @handle('>', '>', filter=navigation_mode)
    def _(event):
        """
        Indent lines.
        """
        buffer = event.current_buffer
        current_row = buffer.document.cursor_position_row
        indent(buffer, current_row, current_row + event.arg)

    @handle('<', '<', filter=navigation_mode)
    def _(event):
        """
        Unindent lines.
        """
        current_row = event.current_buffer.document.cursor_position_row
        unindent(event.current_buffer, current_row, current_row + event.arg)

    @handle('>', filter=selection_mode)
    def _(event):
        """
        Indent selection
        """
        buffer = event.current_buffer
        selection_type = buffer.selection_state.type

        if selection_type == SelectionType.LINES:
            from_, to = buffer.document.selection_range()
            from_, _ = buffer.document.translate_index_to_position(from_)
            to, _ = buffer.document.translate_index_to_position(to)

            indent(buffer, from_ - 1, to, count=event.arg)  # XXX: why does translate_index_to_position return 1-based indexing???

    @handle('<', filter=selection_mode)
    def _(event):
        """
        Unindent selection
        """
        buffer = event.current_buffer
        selection_type = buffer.selection_state.type

        if selection_type == SelectionType.LINES:
            from_, to = buffer.document.selection_range()
            from_, _ = buffer.document.translate_index_to_position(from_)
            to, _ = buffer.document.translate_index_to_position(to)

            unindent(buffer, from_ - 1, to, count=event.arg)

    @handle('O', filter=navigation_mode)
    def _(event):
        """
        Open line above and enter insertion mode
        """
        event.current_buffer.insert_line_above()
        vi_state.input_mode = InputMode.INSERT

    @handle('o', filter=navigation_mode)
    def _(event):
        """
        Open line below and enter insertion mode
        """
        event.current_buffer.insert_line_below()
        vi_state.input_mode = InputMode.INSERT

    @handle('~', filter=navigation_mode)
    def _(event):
        """
        Reverse case of current character and move cursor forward.
        """
        buffer = event.current_buffer
        c = buffer.document.current_char

        if c is not None and c != '\n':
            c = (c.upper() if c.islower() else c.lower())
            buffer.insert_text(c, overwrite=True)

    @handle('#', filter=navigation_mode)
    def _(event):
        """
        Go to previous occurence of this word.
        """
        pass

    @handle('*', filter=navigation_mode)
    def _(event):
        """
        Go to next occurence of this word.
        """
        pass

    @handle('(', filter=navigation_mode)
    def _(event):
        # TODO: go to begin of sentence.
        pass

    @handle(')', filter=navigation_mode)
    def _(event):
        # TODO: go to end of sentence.
        pass

    def change_delete_move_yank_handler(*keys, **kw):
        """
        Register a change/delete/move/yank handlers. e.g.  'dw'/'cw'/'w'/'yw'
        The decorated function should return a ``CursorRegion``.
        This decorator will create both the 'change', 'delete' and move variants,
        based on that ``CursorRegion``.
        """
        no_move_handler = kw.pop('no_move_handler', False)

        # TODO: Also do '>' and '<' indent/unindent operators.
        # TODO: Also "gq": text formatting
        #  See: :help motion.txt
        def decorator(func):
            if not no_move_handler:
                @handle(*keys, filter=navigation_mode)
                @handle(*keys, filter=selection_mode)
                def move(event):
                    """ Create move handler. """
                    region = func(event)
                    event.current_buffer.cursor_position += region.start

            def create_transform_handler(transform_func, *a):
                @handle(*(a + keys), filter=navigation_mode)
                def _(event):
                    """ Apply transformation (uppercase, lowercase, rot13, swap case). """
                    region = func(event)
                    start, end = region.sorted()
                    buffer = event.current_buffer

                    # Transform.
                    buffer.transform_region(
                        buffer.cursor_position + start,
                        buffer.cursor_position + end,
                        transform_func)

                    # Move cursor
                    buffer.cursor_position += (region.end or region.start)

            for k, f in vi_transform_functions:
                create_transform_handler(f, *k)

            @handle('y', *keys, filter=navigation_mode)
            def yank_handler(event):
                """ Create yank handler. """
                region = func(event)
                buffer = event.current_buffer

                start, end = region.sorted()
                substring = buffer.text[buffer.cursor_position + start: buffer.cursor_position + end]

                if substring:
                    event.cli.clipboard.set_text(substring)

            def create(delete_only):
                """ Create delete and change handlers. """
                @handle('cd'[delete_only], *keys, filter=navigation_mode)
                @handle('cd'[delete_only], *keys, filter=navigation_mode)
                def _(event):
                    region = func(event)
                    deleted = ''
                    buffer = event.current_buffer

                    if region:
                        start, end = region.sorted()

                        # Move to the start of the region.
                        buffer.cursor_position += start

                        # Delete until end of region.
                        deleted = buffer.delete(count=end-start)

                    # Set deleted/changed text to clipboard.
                    if deleted:
                        event.cli.clipboard.set_text(deleted)

                    # Only go back to insert mode in case of 'change'.
                    if not delete_only:
                        vi_state.input_mode = InputMode.INSERT

            create(True)
            create(False)
            return func
        return decorator

    @change_delete_move_yank_handler('b')
    def _(event):
        """ Move one word or token left. """
        return CursorRegion(event.current_buffer.document.find_start_of_previous_word(count=event.arg) or 0)

    @change_delete_move_yank_handler('B')
    def _(event):
        """ Move one non-blank word left """
        return CursorRegion(event.current_buffer.document.find_start_of_previous_word(count=event.arg, WORD=True) or 0)

    @change_delete_move_yank_handler('$')
    def key_dollar(event):
        """ 'c$', 'd$' and '$':  Delete/change/move until end of line. """
        return CursorRegion(event.current_buffer.document.get_end_of_line_position())

    @change_delete_move_yank_handler('w')
    def _(event):
        """ 'word' forward. 'cw', 'dw', 'w': Delete/change/move one word.  """
        return CursorRegion(event.current_buffer.document.find_next_word_beginning(count=event.arg) or
                            event.current_buffer.document.end_position)

    @change_delete_move_yank_handler('W')
    def _(event):
        """ 'WORD' forward. 'cW', 'dW', 'W': Delete/change/move one WORD.  """
        return CursorRegion(event.current_buffer.document.find_next_word_beginning(count=event.arg, WORD=True) or
                            event.current_buffer.document.end_position)

    @change_delete_move_yank_handler('e')
    def _(event):
        """ End of 'word': 'ce', 'de', 'e' """
        end = event.current_buffer.document.find_next_word_ending(count=event.arg)
        return CursorRegion(end - 1 if end else 0)

    @change_delete_move_yank_handler('E')
    def _(event):
        """ End of 'WORD': 'cE', 'dE', 'E' """
        end = event.current_buffer.document.find_next_word_ending(count=event.arg, WORD=True)
        return CursorRegion(end - 1 if end else 0)

    @change_delete_move_yank_handler('i', 'w', no_move_handler=True)
    def _(event):
        """ Inner 'word': ciw and diw """
        start, end = event.current_buffer.document.find_boundaries_of_current_word()
        return CursorRegion(start, end)

    @change_delete_move_yank_handler('a', 'w', no_move_handler=True)
    def _(event):
        """ A 'word': caw and daw """
        start, end = event.current_buffer.document.find_boundaries_of_current_word(include_trailing_whitespace=True)
        return CursorRegion(start, end)

    @change_delete_move_yank_handler('i', 'W', no_move_handler=True)
    def _(event):
        """ Inner 'WORD': ciW and diW """
        start, end = event.current_buffer.document.find_boundaries_of_current_word(WORD=True)
        return CursorRegion(start, end)

    @change_delete_move_yank_handler('a', 'W', no_move_handler=True)
    def _(event):
        """ A 'WORD': caw and daw """
        start, end = event.current_buffer.document.find_boundaries_of_current_word(WORD=True, include_trailing_whitespace=True)
        return CursorRegion(start, end)

    @change_delete_move_yank_handler('^')
    def key_circumflex(event):
        """ 'c^', 'd^' and '^': Soft start of line, after whitespace. """
        return CursorRegion(event.current_buffer.document.get_start_of_line_position(after_whitespace=True))

    @change_delete_move_yank_handler('0', no_move_handler=True)
    def key_zero(event):
        """
        'c0', 'd0': Hard start of line, before whitespace.
        (The move '0' key is implemented elsewhere, because a '0' could also change the `arg`.)
        """
        return CursorRegion(event.current_buffer.document.get_start_of_line_position(after_whitespace=False))

    def create_ci_ca_handles(ci_start, ci_end, inner):
                # TODO: 'dab', 'dib', (brackets or block) 'daB', 'diB', Braces.
                # TODO: 'dat', 'dit', (tags (like xml)
        """
        Delete/Change string between this start and stop character. But keep these characters.
        This implements all the ci", ci<, ci{, ci(, di", di<, ca", ca<, ... combinations.
        """
        @change_delete_move_yank_handler('ai'[inner], ci_start, no_move_handler=True)
        @change_delete_move_yank_handler('ai'[inner], ci_end, no_move_handler=True)
        def _(event):
            start = event.current_buffer.document.find_backwards(ci_start, in_current_line=True)
            end = event.current_buffer.document.find(ci_end, in_current_line=True)

            if start is not None and end is not None:
                offset = 0 if inner else 1
                return CursorRegion(start + 1 - offset, end + offset)

    for inner in (False, True):
        for ci_start, ci_end in [('"', '"'), ("'", "'"), ("`", "`"),
                                 ('[', ']'), ('<', '>'), ('{', '}'), ('(', ')')]:
            create_ci_ca_handles(ci_start, ci_end, inner)

    @change_delete_move_yank_handler('{')  # TODO: implement 'arg'
    def _(event):
        """
        Move to previous blank-line separated section.
        Implements '{', 'c{', 'd{', 'y{'
        """
        line_index = event.current_buffer.document.find_previous_matching_line(
            lambda text: not text or text.isspace())

        if line_index:
            index = event.current_buffer.document.get_cursor_up_position(count=-line_index)
        else:
            index = 0
        return CursorRegion(index)

    @change_delete_move_yank_handler('}')  # TODO: implement 'arg'
    def _(event):
        """
        Move to next blank-line separated section.
        Implements '}', 'c}', 'd}', 'y}'
        """
        line_index = event.current_buffer.document.find_next_matching_line(
            lambda text: not text or text.isspace())

        if line_index:
            index = event.current_buffer.document.get_cursor_down_position(count=line_index)
        else:
            index = 0

        return CursorRegion(index)

    @change_delete_move_yank_handler('f', Keys.Any)
    def _(event):
        """
        Go to next occurance of character. Typing 'fx' will move the
        cursor to the next occurance of character. 'x'.
        """
        vi_state.last_character_find = CharacterFind(event.data, False)
        match = event.current_buffer.document.find(event.data, in_current_line=True, count=event.arg)
        return CursorRegion(match or 0)

    @change_delete_move_yank_handler('F', Keys.Any)
    def _(event):
        """
        Go to previous occurance of character. Typing 'Fx' will move the
        cursor to the previous occurance of character. 'x'.
        """
        vi_state.last_character_find = CharacterFind(event.data, True)
        return CursorRegion(event.current_buffer.document.find_backwards(event.data, in_current_line=True, count=event.arg) or 0)

    @change_delete_move_yank_handler('t', Keys.Any)
    def _(event):
        """
        Move right to the next occurance of c, then one char backward.
        """
        vi_state.last_character_find = CharacterFind(event.data, False)
        match = event.current_buffer.document.find(event.data, in_current_line=True, count=event.arg)
        return CursorRegion(match - 1 if match else 0)

    @change_delete_move_yank_handler('T', Keys.Any)
    def _(event):
        """
        Move left to the previous occurance of c, then one char forward.
        """
        vi_state.last_character_find = CharacterFind(event.data, True)
        match = event.current_buffer.document.find_backwards(event.data, in_current_line=True, count=event.arg)
        return CursorRegion(match + 1 if match else 0)

    def repeat(reverse):
        """
        Create ',' and ';' commands.
        """
        @change_delete_move_yank_handler(',' if reverse else ';')
        def _(event):
            # Repeat the last 'f'/'F'/'t'/'T' command.
            pos = 0

            if vi_state.last_character_find:
                char = vi_state.last_character_find.character
                backwards = vi_state.last_character_find.backwards

                if reverse:
                    backwards = not backwards

                if backwards:
                    pos = event.current_buffer.document.find_backwards(char, in_current_line=True, count=event.arg)
                else:
                    pos = event.current_buffer.document.find(char, in_current_line=True, count=event.arg)
            return CursorRegion(pos or 0)
    repeat(True)
    repeat(False)

    @change_delete_move_yank_handler('h')
    @change_delete_move_yank_handler(Keys.Left)
    def _(event):
        """ Implements 'ch', 'dh', 'h': Cursor left. """
        return CursorRegion(event.current_buffer.document.get_cursor_left_position(count=event.arg))

    @change_delete_move_yank_handler('j', no_move_handler=True)
    def _(event):
        """ Implements 'cj', 'dj', 'j', ... Cursor up. """
        return CursorRegion(event.current_buffer.document.get_cursor_down_position(count=event.arg))

    @change_delete_move_yank_handler('k', no_move_handler=True)
    def _(event):
        """ Implements 'ck', 'dk', 'k', ... Cursor up. """
        return CursorRegion(event.current_buffer.document.get_cursor_up_position(count=event.arg))

    @change_delete_move_yank_handler('l')
    @change_delete_move_yank_handler(' ')
    @change_delete_move_yank_handler(Keys.Right)
    def _(event):
        """ Implements 'cl', 'dl', 'l', 'c ', 'd ', ' '. Cursor right. """
        return CursorRegion(event.current_buffer.document.get_cursor_right_position(count=event.arg))

    @change_delete_move_yank_handler('H')
    def _(event):
        """ Implements 'cH', 'dH', 'H'. """
        # Vi moves to the start of the visible region.
        # cursor position 0 is okay for us.
        return CursorRegion(-len(event.current_buffer.document.text_before_cursor))

    @change_delete_move_yank_handler('L')
    def _(event):
        # Vi moves to the end of the visible region.
        # cursor position 0 is okay for us.
        return CursorRegion(len(event.current_buffer.document.text_after_cursor))

    @change_delete_move_yank_handler('%')
    def _(event):
        """
        Implements 'c%', 'd%', '%, 'y%' (Move to corresponding bracket.)
        If an 'arg' has been given, go this this % position in the file.
        """
        buffer = event.current_buffer

        if event._arg:
            # If 'arg' has been given, the meaning of % is to go to the 'x%'
            # row in the file.
            if 0 < event.arg <= 100:
                absolute_index = buffer.document.translate_row_col_to_index(
                    int(event.arg * buffer.document.line_count / 100), 0)
                return CursorRegion(absolute_index - buffer.document.cursor_position)
            else:
                return CursorRegion(0)  # Do nothing.

        else:
            # Move to the corresponding opening/closing bracket (()'s, []'s and {}'s).
            return CursorRegion(buffer.document.matching_bracket_position)

    @change_delete_move_yank_handler('|')
    def _(event):
        # Move to the n-th column (you may specify the argument n by typing
        # it on number keys, for example, 20|).
        return CursorRegion(event.current_buffer.document.get_column_cursor_position(event.arg))

    @change_delete_move_yank_handler('g', 'g')
    def _(event):
        """
        Implements 'gg', 'cgg', 'ygg'
        """
        # Move to the top of the input.
        return CursorRegion(event.current_buffer.document.home_position)

    @change_delete_move_yank_handler('g', '_')
    def _(event):
        """
        Go to last non-blank of line.
        'g_', 'cg_', 'yg_', etc..
        """
        return CursorRegion(
            event.current_buffer.document.last_non_blank_of_current_line_position())

    @change_delete_move_yank_handler('g', 'e')
    def _(event):
        """
        Go to last character of previous word.
        'ge', 'cge', 'yge', etc..
        """
        return CursorRegion(
            event.current_buffer.document.find_start_of_previous_word(count=event.arg) or 0)

    @change_delete_move_yank_handler('g', 'E')
    def _(event):
        """
        Go to last character of previous WORD.
        'gE', 'cgE', 'ygE', etc..
        """
        return CursorRegion(
            event.current_buffer.document.find_start_of_previous_word(
                count=event.arg, WORD=True) or 0)

    @handle(Keys.Any, filter=navigation_mode)
    @handle(Keys.Any, filter=selection_mode)
    def _(event):
        """
        Always handle numberics in navigation mode as arg.
        """
        if event.data in '123456789' or (event._arg and event.data == '0'):
            event.append_to_arg_count(event.data)
        elif event.data == '0':
            buffer = event.current_buffer
            buffer.cursor_position += buffer.document.get_start_of_line_position(after_whitespace=False)

    @handle(Keys.Any, filter=replace_mode)
    def _(event):
        """
        Insert data at cursor position.
        """
        event.current_buffer.insert_text(event.data, overwrite=True)

    def create_selection_transform_handler(keys, transform_func):
        """
        Apply transformation on selection (uppercase, lowercase, rot13, swap case).
        """
        @handle(*keys, filter=selection_mode)
        def _(event):
            range = event.current_buffer.document.selection_range()
            if range:
                event.current_buffer.transform_region(range[0], range[1], transform_func)

    for k, f in vi_transform_functions:
        create_selection_transform_handler(k, f)

    @handle(Keys.ControlX, Keys.ControlL, filter=insert_mode)
    def _(event):
        """
        Pressing the ControlX - ControlL sequence in Vi mode does line
        completion based on the other lines in the document and the history.
        """
        event.current_buffer.start_history_lines_completion()

    @handle(Keys.ControlX, Keys.ControlF, filter=insert_mode)
    def _(event):
        """
        Complete file names.
        """
        # TODO
        pass


def load_vi_system_bindings(registry, vi_state, filter=None, system_buffer_name='system'):
    assert isinstance(vi_state, ViState)

    has_focus = filters.HasFocus(system_buffer_name)
    navigation_mode = ViStateFilter(vi_state, InputMode.NAVIGATION) & ~ filters.HasSelection()

    handle = create_handle_decorator(registry, filter)

    @handle('!', filter=~has_focus & navigation_mode)
    def _(event):
        """
        '!' opens the system prompt.
        """
        event.cli.focus_stack.push(system_buffer_name)
        vi_state.input_mode = InputMode.INSERT

    @handle(Keys.Escape, filter=has_focus)
    @handle(Keys.ControlC, filter=has_focus)
    def _(event):
        """
        Cancel system prompt.
        """
        vi_state.input_mode = InputMode.NAVIGATION
        event.cli.buffers[system_buffer_name].reset()
        event.cli.focus_stack.pop()

    @handle(Keys.ControlJ, filter=has_focus)
    def _(event):
        """
        Run system command.
        """
        vi_state.input_mode = InputMode.NAVIGATION

        system_buffer = event.cli.buffers[system_buffer_name]
        event.cli.run_system_command(system_buffer.text)
        system_buffer.reset(append_to_history=True)

        # Focus previous buffer again.
        event.cli.focus_stack.pop()


def load_vi_search_bindings(registry, vi_state, filter=None, search_buffer_name='search'):
    assert isinstance(vi_state, ViState)

    has_focus = filters.HasFocus(search_buffer_name)
    navigation_mode = ~has_focus & (ViStateFilter(vi_state, InputMode.NAVIGATION) | filters.HasSelection())
    handle = create_handle_decorator(registry, filter)

    @handle('/', filter=navigation_mode)
    @handle(Keys.ControlS)
    def _(event):
        """
        Vi-style forward search.
        """
        vi_state.search_direction = direction = IncrementalSearchDirection.FORWARD
        vi_state.input_mode = InputMode.INSERT

        if event.cli.focus_stack.current != search_buffer_name:
            event.cli.focus_stack.push(search_buffer_name)

        event.cli.buffers[event.cli.focus_stack.previous].incremental_search(direction)

    @handle('?', filter=navigation_mode)
    @handle(Keys.ControlR)
    def _(event):
        """
        Vi-style backward search.
        """
        vi_state.search_direction = direction = IncrementalSearchDirection.BACKWARD
        vi_state.input_mode = InputMode.INSERT

        if event.cli.focus_stack.current != search_buffer_name:
            event.cli.focus_stack.push(search_buffer_name)

        event.cli.buffers[event.cli.focus_stack.previous].incremental_search(direction)

    @handle(Keys.ControlJ, filter=has_focus)
    def _(event):
        """
        Enter at the / or ? prompt.
        """
        search_buffer = event.cli.buffers[search_buffer_name]
        vi_state.input_mode = InputMode.NAVIGATION

        # Add query to history of search line.
        search_buffer.add_to_history()
        search_buffer.reset()

        # Focus previous document again.
        event.cli.focus_stack.pop()

    @handle(Keys.Any, filter=has_focus)
    def _(event):
        """
        Insert text after the / or ? prompt.
        """
        event.cli.current_buffer.insert_text(event.data)

        # Set current search search text as line search text.
        buffer = event.cli.buffers[event.cli.focus_stack.previous]
        buffer.set_search_text(event.cli.current_buffer.text)

    @handle(Keys.Escape, filter=has_focus)
    @handle(Keys.ControlC, filter=has_focus)
    def _(event):
        """
        Cancel search.
        """
        vi_state.input_mode = InputMode.NAVIGATION

        event.cli.focus_stack.pop()
        event.current_buffer.exit_isearch(restore_original_line=True)

        event.cli.buffers[search_buffer_name].reset()

# TODO: Maybe handle insert/backspace through Change event.

#    @handle(Keys.Backspace, filter=has_focus)
#    def _(event):
#        """
#        Backspace at the vi-search prompt.
#        """
#        search_line = event.cli.buffers['search']
#
#        if search_line.text:
#            search_line.delete_before_cursor()
#            event.current_buffer.set_search_text(search_line.text)
#        else:
#            # If no text after the prompt, cancel search.
#            event.current_buffer.exit_isearch(restore_original_line=True)
#            search_line.reset()
#            event.input_processor.pop_input_mode()
