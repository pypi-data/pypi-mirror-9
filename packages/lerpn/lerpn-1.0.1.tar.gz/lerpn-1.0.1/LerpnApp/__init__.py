#!/usr/bin/python

# Written in 2015 by Christopher Pavlina.
###############################################################################
#
# This software is free. Do whatever the fuck you want with it. Copy it, change
# it, steal it, strip away this notice, print it and tear it into confetti to
# throw at random dudes on the street. Really, I don't care.

import curses
from . import nums, env, tui

def wrapped_main (stdscr):
    curses.nonl ()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    error = None
    stack = nums.UndoStack ()
    while True:
        stdscr.clear ()
        tui.RPN_drawstack (stack, stdscr)
        error = tui.RPN_prompt (stack, error, stdscr)

def main ():
    curses.wrapper (wrapped_main)

if __name__ == "__main__":
    main ()
