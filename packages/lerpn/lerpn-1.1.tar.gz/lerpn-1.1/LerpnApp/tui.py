"""Code dealing directly with the text user interface.

Currently this ties in heavily with curses. Eventually, curses will be
abstracted out.
"""

import curses
import string
import sys
from .commands import SINGLE_KEY_COMMANDS, COMMANDS
from . import env, nums, curses_stuff

def format_stack(stack, recurse=True, firstcall=True):
    """Converts a single stack to a list of lines of text.
    If the stack has a parent and recurse is true, draw the parents
    as well.

    Also returns a list of x coordinates where dividers should be
    drawn.
    """

    lines = []

    for i, item in enumerate(stack):
        tag = None

        tag = getattr(item, "tag", None)

        formatted = env.FORMAT.format(item)
        stack_n = i

        if tag is None and firstcall:
            lines.append("%3d  %20s" % (stack_n, formatted))
        elif tag is None:
            lines.append("| %20s" % formatted)
        elif firstcall:
            lines.append("%3d  %20s : %s" % (stack_n, formatted, tag))
        else:
            lines.append("| %20s : %s" % (formatted, tag))

    lines = lines[::-1]

    if recurse and stack.parent is not None:
        parent_lines, parent_dividers = format_stack(stack.parent, firstcall=False)

        # Line up lines at the bottom
        if len(lines) < len(parent_lines):
            lines.extend([""] * (len(parent_lines) - len(lines)))
        elif len(parent_lines) < len(lines):
            parent_lines.extend([""] * (len(lines) - len(parent_lines)))

        # Concatenate
        if firstcall:
            concat_len = 35
        else:
            concat_len = 15

        joined_lines = []
        for i, j in zip(lines, parent_lines):
            if len(i) < concat_len:
                i += " " *(concat_len - len(i))
            i = i[:concat_len]
            joined_lines.append(i + j)
        return joined_lines, [concat_len] + [i + concat_len for i in parent_dividers]

    return lines, []


def draw_stack(stack, window):
    """Draw the stack onto a curses window.
    """

    lines, dividers = format_stack(stack)

    curses_stuff.draw_text(window, lines, offset=-1, xoffset=0, padding=2)

    for xoff in dividers:
        curses_stuff.draw_vline(window, xoff, 2, -1)

    curses.doupdate()

def get_single_key_command(key):
    """
    Return a single-key command for the key, or None.
    """
    if key > 127:
        lookup_key = key
    else:
        try:
            lookup_key = chr(key)
        except ValueError:
            lookup_key = key
    return SINGLE_KEY_COMMANDS.get(lookup_key, None)

def do_command(stack, cmd, arg):
    """ Execute the command on the stack in an exception wrapper.

    Returns None if no exception, or sys.exc_info() if there was one.
    """

    # pylint: disable=broad-except
    # We want to catch any exception here - it'll be handled properly.

    try:
        stack.undopush()
        rtn = cmd(stack, arg)
    except Exception:
        stack.undo()
        return sys.exc_info()
    else:
        assert rtn is None
        return None

ENTER_KEYS = [curses.KEY_ENTER, 10, 13]
BACKSPACE_KEYS = [curses.KEY_BACKSPACE, 127, 8]

def do_edit(key, strbuf):
    """
    Line-edit.
    Returns "BACKSPACE", "ENTER", or None
    """

    if key in BACKSPACE_KEYS:
        if len(strbuf):
            del strbuf[-1]
        return "BACKSPACE"

    if key in ENTER_KEYS:
        return "ENTER"

    try:
        strbuf.append(chr(key))
    except ValueError:
        pass

    return None

def do_exit(stack, window):
    """Perform the exit action.

    In this case, the stack is formatted to stdout,
    then we exit.
    """

    def exit_helper():
        for item in stack:
            if hasattr(item, "magnitude"):
                mag = item.magnitude
            else:
                mag = item

            mag_fmt = nums.NaturalMode.format(mag)
            item_fmt = env.FORMAT.format(item)
            print("%s\t%s" % (mag_fmt, item_fmt))

    # Using atexit allows us to register the function to be called after
    # curses.wrapper() performs cleanup
    import atexit
    atexit.register(exit_helper)

    sys.exit(0)

STATES = [
    "FIRSTCHAR",    # first character determines the mode
    "NUMERIC",      # parsing numeric
    "NUMUNIT",      # parsing unit inside numeric
    "COMMAND",      # parsing command
    "STRING",       # parsing string
    ]
def prompt_cycle(stack, error, window):
    """Displays the prompt and executes a user action from it.
    stack:  buffer current UndoStack
    error:  any error text returned from the _previous_ RPN_prompt, or None
    window: curses window

    returns any error text from the command, or None.
    """

    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    #
    # Yes, it's a big function. There's no reason for it not to be, though -
    # none of its parts will ever be used elsewhere. Refactoring it would be
    # a waste of time.

    if error is not None:
        env.ERROR = error
        window.addstr(0, 0, "ERROR: %s" % str(error[1]))

    state = "FIRSTCHAR"
    strbuf = []

    while True:
        assert state in STATES
        draw_stack(stack, window)
        prompt_line = "? " + "".join(strbuf)
        if not curses_stuff.draw_textline(window, prompt_line, -1, 0, True):
            curses_stuff.do_resize(window)
            return
        curses.doupdate()

        try:
            key, char = curses_stuff.getkey(window)
        except KeyboardInterrupt:
            do_exit(stack, window)

        if state == "FIRSTCHAR":

            # Try single-key commands first
            cmd = get_single_key_command(key)
            if cmd is not None:
                return do_command(stack, cmd, None)

            if char is None:
                continue

            if char in string.digits + "_.":
                strbuf.append(char)
                state = "NUMERIC"

            if char == "'":
                strbuf.append(char)
                state = "COMMAND"

            elif char == '"':
                strbuf.append(char)
                state = "STRING"

        elif state == "NUMERIC":

            cmd = get_single_key_command(key)

            # Make exceptions for letters that are typed in numbers but might also be
            # single-letter commands
            if char is not None and(char in "eEjJ"):
                cmd = None

            for i in "eEjJ":
                if i in strbuf and char == "-":
                    cmd = None

            edit_type = do_edit(key, strbuf)
            if (edit_type == "ENTER" or
                    (cmd is not None and edit_type != "BACKSPACE") or
                    char == "'"):

                if (cmd is not None and strbuf and edit_type != "ENTER") or char == "'":
                    # Do not include command in number
                    del strbuf[-1]

                # pylint: disable=broad-except
                # We want to catch any exception here - it'll be handled properly.
                try:
                    parsed = nums.num_parser(''.join(strbuf))
                except Exception:
                    return sys.exc_info()
                else:
                    stack.append(parsed)

                    if char == "'":
                        strbuf[:] = "'"
                        state = "COMMAND"
                        continue
                    if edit_type != "ENTER" and cmd is not None:
                        return do_command(stack, cmd, None)
                    else:
                        return None

            if strbuf and(strbuf[-1] == " " or strbuf[-1] == '"'):
                state = "NUMUNIT"

            if not strbuf:
                state = "FIRSTCHAR"

            if char is None:
                continue

        elif state == "NUMUNIT":
            # Like numeric, but since units can contain letters that have
            # "single-unit commands" in them, ignore those.

            if do_edit(key, strbuf) == "ENTER" or char == "'":
                # pylint: disable=broad-except
                # We want to catch any exception here - it'll be handled properly.
                if char == "'":
                    del strbuf[-1]
                try:
                    parsed = nums.num_parser(''.join(strbuf))
                except Exception:
                    return sys.exc_info()

                stack.append(parsed)

                if char == "'":
                    strbuf[:] = "'"
                    state = "COMMAND"
                    continue
                return

            if not strbuf:
                state = "FIRSTCHAR"

        elif state == "COMMAND":

            if do_edit(key, strbuf) == "ENTER":
                command_string = ''.join(strbuf)
                # pylint: disable=unused-variable
                cmdname, delim, arg = command_string.partition(" ")
                cmd = COMMANDS.get(cmdname, None)
                if cmd is not None:
                    return do_command(stack, cmd, arg)
                elif not len(strbuf):
                    return None
                else:
                    try:
                        raise KeyError("Command not found: %s" % ''.join(strbuf))
                    except KeyError:
                        return sys.exc_info()

            if not strbuf:
                state = "FIRSTCHAR"

        elif state == "STRING":
            if do_edit(key, strbuf) == "ENTER":
                stack.append(''.join(strbuf).lstrip('"'))
                return None

            if not strbuf:
                state = "FIRSTCHAR"
