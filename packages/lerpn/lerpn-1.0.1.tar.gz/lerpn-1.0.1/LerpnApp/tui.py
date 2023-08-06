import curses
import string
import sys
from .commands import SINGLE_LETTER_COMMANDS, COMMANDS
from . import env, nums

def RPN_drawstack (stack, window):
    """Draw the stack onto a curses window.
    """
    for i, item in enumerate (stack):
        row = curses.LINES - len (stack) - 2 + i
        if row < 1:
            continue

        tag = None
        mode = 0
        
        if isinstance (item, nums.Tagged):
            tag = item.tag
            item = item.num

        if hasattr (item, "magnitude"):
            # TODO: HACK
            # pint will add a way to format just the abbreviated unit in 0.7.
            # For now, I'll format a known magnitude and then remove the known
            # magnitude
            
            one_magnitude_unit = format (nums.UREG.Quantity (1, item.units), "~")
            assert one_magnitude_unit.startswith ("1 ")
            units_abbrev = one_magnitude_unit[2:]

            if env.FORMAT == "eng":
                formatted = nums.eng (item.magnitude, env.SIGFIGS) + " " + units_abbrev
            else:
                formatted = "%e %s" % (item.magnitude, units_abbrev)

        elif isinstance (item, float):
            if env.FORMAT == "eng":
                formatted = nums.eng (item, env.SIGFIGS)
            else:
                formatted = "%e" % item

        elif isinstance (item, str):
            formatted = item
            mode = curses.color_pair(1)

        else:
            formatted = repr(item)

        if tag is None:
            window.addstr (row, 0, "%3d  %20s" % (i, formatted), mode)
        else:
            window.addstr (row, 0, "%3d  %20s : %s" % (i, formatted, tag), mode)

    curses.doupdate ()

def do_resize (window):
    """Handles redrawing the window if it has been resized.
    """
    resize = curses.is_term_resized (curses.LINES, curses.COLS)
    if resize:
        y, x = window.getmaxyx ()
        window.clear ()
        curses.resizeterm (y, x)
        curses.doupdate ()

def get_single_key_command (key):
    """
    Return a single-key command for the key, or None.
    """
    if key > 127:
        lookup_key = key
    else:
        try:
            lookup_key = chr (key)
        except ValueError:
            lookup_key = key
    return SINGLE_LETTER_COMMANDS.get (lookup_key, None)

def do_command (stack, cmd):
    try:
        stack.undopush ()
        cmd[0] (stack)
    except Exception:
        stack.undo ()
        return sys.exc_info ()
    else:
        return None

ENTER_KEYS = [curses.KEY_ENTER, 10, 13]
BACKSPACE_KEYS = [curses.KEY_BACKSPACE, 127, 8]

def do_edit (key, strbuf):
    """
    Line-edit.
    Returns "BACKSPACE", "ENTER", or None
    """

    if key in BACKSPACE_KEYS:
        if len (strbuf):
            del strbuf[-1]
        return "BACKSPACE"

    if key in ENTER_KEYS:
        return "ENTER"

    try:
        strbuf.append (chr (key))
    except ValueError:
        pass

    return None

def RPN_prompt (stack, error, window):
    """Displays the prompt.
    stack:  buffer current UndoStack
    error:  any error text returned from the _previous_ RPN_prompt, or None
    window: curses window
    
    returns any error text from the command, or None.
    """

    if error is not None:
        env.ERROR = error
        window.addstr (0, 0, "ERROR: %s" % str (error[1]))

    STATES = [
        "FIRSTCHAR",    # first character determines the mode
        "NUMERIC",      # parsing numeric
        "NUMUNIT",      # parsing unit inside numeric
        "COMMAND",      # parsing command
        "STRING",       # parsing string
        ]
    state = "FIRSTCHAR"
    strbuf = []

    while True:
        assert state in STATES
        RPN_drawstack (stack, window)
        try:
            window.move (curses.LINES - 1, 0)
        except Exception:
            # Exception happens here sometimes on window resize. Not always,
            # but it seems to happen particularly when i3 pops a window out
            # from tiled->floating
            do_resize (window)
            return
        window.addstr ("? ")
        for i in strbuf:
            window.addstr (i)
        window.clrtoeol ()
        curses.doupdate ()

        try:
            key = window.getch ()
        except KeyboardInterrupt:
            sys.exit (0)
        try:
            char = chr (key)
        except ValueError:
            char = None

        if state == "FIRSTCHAR":

            # Try single-key commands first
            cmd = get_single_key_command (key)
            if cmd is not None:
                return do_command (stack, cmd)

            if char is None:
                continue

            if char in string.digits + "_.":
                strbuf.append (char)
                state = "NUMERIC"

            if char == "'":
                strbuf.append (char)
                state = "COMMAND"

            elif char == '"':
                strbuf.append (char)
                state = "STRING"

        elif state == "NUMERIC":

            cmd = get_single_key_command (key)

            # Make exception for 'e' so that we can type sci notation
            if char == "e" or char == "E" or (("e" in strbuf or "E" in strbuf) and char == "-"):
                cmd = None

            edit_type = do_edit (key, strbuf)
            if edit_type == "ENTER" or (cmd is not None and edit_type != "BACKSPACE"):
                if cmd is not None and strbuf and edit_type != "ENTER":
                    # Do not include command in number
                    del strbuf[-1]
                try:
                    if strbuf[0] == "_":
                        strbuf[0] = "-"
                    f = nums.num_parser (''.join(strbuf))
                except Exception:
                    return sys.exc_info ()
                else:
                    stack.append (f)

                    if edit_type != "ENTER" and cmd is not None:
                        return do_command (stack, cmd)
                    else:
                        return None

            if strbuf and (strbuf[-1] == " " or strbuf[-1] == '"'):
                state = "NUMUNIT"

            if not strbuf:
                state = "FIRSTCHAR"

            if char is None:
                continue

        elif state == "NUMUNIT":
            # Like numeric, but since units can contain letters that have
            # "single-unit commands" in them, ignore those.

            if do_edit (key, strbuf) == "ENTER":
                try:
                    if strbuf[0] == "_":
                        strbuf[0] = "-"
                    f = nums.num_parser (''.join(strbuf))
                except Exception:
                    return sys.exc_info ()
                else:
                    stack.append (f)
                    return

            if not strbuf:
                state = "FIRSTCHAR"

        elif state == "COMMAND":

            if do_edit (key, strbuf) == "ENTER":
                command_string = ''.join (strbuf)
                cmd_and_args = command_string.partition(" ")
                cmd = COMMANDS.get (cmd_and_args[0], None)
                if cmd is not None:
                    try:
                        stack.undopush ()
                        cmd[0] (stack, cmd_and_args[2])
                    except Exception:
                        stack.undo ()
                        return sys.exc_info ()
                    else:
                        return None
                elif not len (strbuf):
                    return None
                else:
                    try:
                        raise Exception ("Command not found: %s" % ''.join(strbuf))
                    except Exception:
                        return sys.exc_info ()

            if not strbuf:
                state = "FIRSTCHAR"
            
        elif state == "STRING":
            if do_edit (key, strbuf) == "ENTER":
                stack.append (''.join (strbuf).lstrip('"'))
                return None

            if not strbuf:
                state = "FIRSTCHAR"
