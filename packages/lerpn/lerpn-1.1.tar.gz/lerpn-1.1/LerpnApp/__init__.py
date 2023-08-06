"""lerpn application module

To run lerpn, call main().
"""

# Written in 2015 by Christopher Pavlina.
###############################################################################
#
# This software is free. Do whatever the fuck you want with it. Copy it, change
# it, steal it, strip away this notice, print it and tear it into confetti to
# throw at random dudes on the street. Really, I don't care.

import curses
from . import nums, env, tui

def wrapped_main(stdscr):
    """main function to be wrapped by curses.wrapper
    """
    curses.nonl()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    error = None
    env.STACK = nums.UndoStack()
    while True:
        stdscr.clear()
        error = tui.prompt_cycle(env.STACK, error, stdscr)

def main():
    """call this to launch lerpn
    """
    curses.wrapper(wrapped_main)

def gen_commands_md():
    """generate a Markdown reference of all commands"""

    from . import commands, curses_stuff

    print("# Quick Command Reference")
    print()
    print("This list is auto-generated from the code, and contains the same")
    print("text you would see in the in-program help box.")
    print()
    print("## Single-key commands")
    print()
    print("Key | Description")
    print("--- | -----------")
    for cmd in commands.SINGLE_KEY_COMMANDS:
        cmd_name = curses_stuff.KEY_TO_NAME.get(cmd, "`%s`" % cmd)
        cmd_desc = commands.SINGLE_KEY_COMMANDS[cmd].__doc__.partition("\n")[0]
        print("%s | %s" % (cmd_name, cmd_desc))
    print()

    print("## Long commands")
    print()
    print("Name | Description")
    print("---- | -----------")
    for cmd in commands.COMMANDS:
        if isinstance(cmd, int):
            cmd_name = ""
            cmd_desc = "**%s**" % commands.COMMANDS[cmd]
        else:
            cmd_name = "`%s`" % cmd
            cmd_desc = commands.COMMANDS[cmd].__doc__.partition("\n")[0]
        print("%s | %s" % (cmd_name, cmd_desc))
    print()

if __name__ == "__main__":
    main()
