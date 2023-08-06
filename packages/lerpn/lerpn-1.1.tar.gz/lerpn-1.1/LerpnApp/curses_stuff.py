"""Curses utilities.
"""

import curses

# Reference of nonprintables to printable names
KEY_TO_NAME = {
    "\x7f": "[0x7f]",
    "\x08": "[0x08]",
    curses.KEY_BACKSPACE: "[bksp]",
    "\r": "[CR]",
    "\n": "[LF]",
    curses.KEY_ENTER: "[enter]",
    curses.KEY_UP: "[up]",
    curses.KEY_DOWN: "[down]",
    curses.KEY_LEFT: "[left]",
    curses.KEY_RIGHT: "[right]",
    curses.KEY_PPAGE: "[pgup]",
    curses.KEY_NPAGE: "[pgdn]",
    curses.KEY_HOME: "[home]",
    curses.KEY_END: "[end]",
}

class CursesScrollBox(object):
    """Displays some text in a scroll box."""

    def __init__(self, width, height):
        """Initialize.

        @param width - desired width: positive for absolute width, negative
                    for margin around window edge
        @param height - desired height: positive for absolute height,
                    negative for margin around window edge
        """
        self.width = width
        self.height = height
        self.title = ""
        self.text = ""
        self.vpos = 0
        self.hpos = 0

        self._width = None
        self._height = None
        self._xoff = None
        self._yoff = None

    def set_text(self, text):
        """Set the text displayed in the scroll box. This can be a string, which
        will be split into lines, or a list of lines"""

        # Split the text?
        if isinstance(text, str):
            text_split = text.split("\n")
        elif isinstance(text, list):
            text_split = text
        else:
            raise TypeError("Text must be list or str")

        # Tab-expand the text so it horizontally scrolls nicely
        lines = []
        for line in text_split:
            new_line = []
            col = 0
            for char in line:
                col += 1
                if char == "\t":
                    n_spaces = 8 - (col - 1) % 8
                    new_line.extend([" "] * n_spaces)
                    col += n_spaces - 1
                else:
                    new_line.append(char)
            lines.append(''.join(new_line))
        self.text = lines

    def set_title(self, title):
        """Set the title to be displayed at the top."""
        self.title = title

    def show(self):
        """
        Display the window on the curses display
        """
        # pylint: disable=no-member
        # curses.COLS, curses.LINES are populated after load

        if self.width < 0:
            self._width = curses.COLS + self.width
        else:
            self._width = self.width
        if self.height < 0:
            self._height = curses.LINES + self.height
        else:
            self._height = self.height
        self._xoff = curses.COLS // 2 - self._width // 2
        self._yoff = curses.LINES // 2 - self._height // 2

        curses.curs_set(0)
        curses.doupdate()
        window = curses.newwin(self._height, self._width, self._yoff, self._xoff)

        while self._show(window):
            pass

        curses.curs_set(1)

    def _show(self, window):
        """
        Used internally. One cycle of the display loop: renders the box, then
        grabs a keypress. Return value is True if we want to loop around again.
        """

        # pylint: disable=too-many-branches

        window.clear()
        window.move(1, 2)
        window.addstr(self.title)
        window.keypad(1)

        view_lines = self.text[self.vpos:self.vpos+self._height - 4]

        max_line_len = max(len(i) for i in self.text)

        for idx, line in enumerate(view_lines):
            window.move(idx + 3, 2)
            # Padding all lines to max length fixes horizontal scrolling of short
            # lines
            display_line = line + " " * (max_line_len - len(line))
            window.addstr(display_line[self.hpos:self._width - 2 + self.hpos])

        if self.vpos > 0:
            window.move(2, self._width - 3)
            window.addstr("+")
        if self.vpos + self._height < len(self.text) + 4:
            window.move(self._height - 2, self._width - 3)
            window.addstr("+")

        if len(self.text) < self._height - 2:
            yscroll_limit = 0
        else:
            yscroll_limit = len(self.text) - self._height // 2
        xscroll_limit = max(len(i) for i in self.text) - self._width // 2

        window.border()

        try:
            key = window.getch()
        except KeyboardInterrupt:
            return False
        if key == curses.KEY_UP:
            self.vpos = max(self.vpos - 1, 0)
        elif key == curses.KEY_DOWN:
            self.vpos = min(self.vpos + 1, yscroll_limit)
        elif key == curses.KEY_PPAGE:
            self.vpos = max(self.vpos - (self._height // 2), 0)
        elif key == curses.KEY_NPAGE:
            self.vpos = min(self.vpos + (self._height // 2), yscroll_limit)
        elif key == curses.KEY_HOME:
            self.vpos = 0
        elif key == curses.KEY_END:
            self.vpos = yscroll_limit
        elif key == curses.KEY_LEFT:
            self.hpos = max(self.hpos - 5, 0)
        elif key == curses.KEY_RIGHT:
            self.hpos = min(self.hpos + 5, xscroll_limit)
            return True
        else:
            return False
        return True

def draw_text(window, lines, offset, xoffset, padding):
    """Draw a list of text lines onto the window.

    @param window - curses window
    @param lines - list of lines
    @param offset - line number to start at. Negative to start at bottom
    @param xoffset - horizontal offset
    @param padding - distance from other end at which to stop
    """

    w_height, w_width = window.getmaxyx()
    lines_wclamp = [i[:w_width] for i in lines]
    lines_hwclamp = lines_wclamp[:(w_height - abs(offset) - padding)]

    for idx, line in enumerate(lines_hwclamp):
        if offset < 0:
            yoffset = w_height - idx + offset - 1
        else:
            yoffset = idx + offset
        window.addstr(yoffset, xoffset, line)

def draw_vline(window, xpos, ystart, height):
    """Draw a vertical line onto the window

    @param window - curses window
    @param xpos - x coordinate (pos from left, neg from right)
    @param ystart - y coordinate (pos from top, neg from bottom)
    @param height - line height (pos absolute, neg relative to window height)
    """

    w_height, w_width = window.getmaxyx()

    if xpos < 0:
        xpos += w_width

    if height < 0:
        height += w_height

    if ystart < 0:
        ystart = w_height - height + ystart

    # pylint: disable=no-member
    # ACS_VLINE is populated at load
    window.vline(ystart, xpos, curses.ACS_VLINE, height)

def draw_textline(window, line, yoff, xoff, clearline=False):
    """Draw a line of text onto the window

    @param window - curses window
    @param line - line of text
    @param yoff - y offset, pos from top, neg from bottom
    @param xoff - x offset, pos from left, neg from right
    @param clearline - True to clear the rest of the line
    @return True on success (can fail of yoff/xoff is invalid)
    """

    w_height, w_width = window.getmaxyx()

    if yoff < 0:
        yoff += w_height
    if xoff < 0:
        xoff += w_width

    try:
        window.move(yoff, xoff)
    except curses.error:
        return False

    window.addstr(line)
    if clearline:
        window.clrtoeol()

    return True

def getkey(window):
    """Get a keypress from the window.

    @return keycode, character  - character will be None if there is no match
    """

    key = window.getch()
    try:
        char = chr(key)
    except ValueError:
        char = None
    return key, char

def do_resize(window):
    """Handles redrawing the window if it has been resized.
    """
    # pylint: disable=no-member
    # curses.LINES,COLS populated at load
    resize = curses.is_term_resized(curses.LINES, curses.COLS)
    if resize:
        height, width = window.getmaxyx()
        window.clear()
        curses.resizeterm(height, width)
        curses.doupdate()
