import curses

class CursesScrollBox (object):
    """Displays some text in a scroll box."""
    def __init__ (self, width, height):
        """Initialize.

        @param width - desired width: positive for absolute width, negative
                    for margin around window edge
        @param height - desired height: positive for absolute height,
                    negative for margin around window edge
        """
        self.w = width
        self.h = height
        self.title = ""
        self.pos = 0

    def set_text (self, text):
        self.text = text

    def set_title (self, title):
        self.title = title

    def show (self):
        if self.w < 0:
            self._w = curses.COLS + self.w
        else:
            self._w = self.w
        if self.h < 0:
            self._h = curses.LINES + self.h
        else:
            self._h = self.h
        self._x = curses.COLS // 2 - self._w // 2
        self._y = curses.LINES // 2 - self._h // 2

        curses.curs_set (0)
        curses.doupdate ()
        self.win = curses.newwin (self._h, self._w, self._y, self._x)

        while self._show ():
            pass

        curses.curs_set (1)

    def _show (self):
        self.win.clear ()
        self.win.move (1, 2)
        self.win.addstr (self.title)
        self.win.keypad (1)

        if isinstance(self.text, str):
            lines = self.text.split("\n")
        elif isinstance(self.text, list):
            lines = self.text
        else:
            raise TypeError ("Text must be list or str")
        view_lines = lines[self.pos:self.pos+self._h - 4]

        for y, line in enumerate (view_lines):
            self.win.move (y + 3, 2)
            self.win.addstr (line.rstrip()[0:self._w])

        if self.pos > 0:
            self.win.move (2, self._w - 3)
            self.win.addstr ("+")
        if self.pos + self._h < len (lines) + 4:
            self.win.move (self._h - 2, self._w - 3)
            self.win.addstr ("+")

        scroll_limit = len (lines) - self._h // 2

        self.win.border ()

        try:
            key = self.win.getch ()
        except KeyboardInterrupt:
            return False
        if key == curses.KEY_UP:
            self.pos = max(self.pos - 1, 0)
        elif key == curses.KEY_DOWN:
            self.pos = min(self.pos + 1, scroll_limit)
        elif key == curses.KEY_PPAGE:
            self.pos = max(self.pos - 10, 0)
        elif key == curses.KEY_NPAGE:
            self.pos = min(self.pos + 10, scroll_limit)
        else:
            return False
        return True
