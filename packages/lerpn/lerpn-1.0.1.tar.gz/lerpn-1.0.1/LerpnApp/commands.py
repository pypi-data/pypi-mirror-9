import collections
import curses
import math

from . import nums, env
from .curses_stuff import CursesScrollBox

# Not all Python versions have log2
if not hasattr (math, "log2"):
    math.log2 = lambda x: math.log (x, 2)

###############################################################################
# COMMAND GENERATORS
#
# Use these to generate common cases, rather than implementing from scratch.

def BINARY (f):
    """Create a binary operator from a lambda function."""
    def cmd (stack, arg=None):
        y = stack.pop ()
        x = stack.pop ()
        stack.append (f (x, y))
    return cmd

def UNARY (f):
    """Create a unary operator from a lambda function.
    The unary operators know how to handle tagged numbers - they reapply the
    same tag after performing the operation."""
    def cmd (stack, arg=None):
        x = stack.pop ()
        if isinstance(x, nums.Tagged):
            newtagged = nums.Tagged(f(x.num), x.tag)
            stack.append (newtagged)
        else:
            stack.append (f (x))
    return cmd

def DEGREE_TRIG (f):
    """Create a unary trig operator that accepts degrees.
    
    This has to be handled specially because pint supports degrees/radians,
    performing the conversion automatically. We have to avoid double-converting,
    and also work in the absence of pint.
    """
    def g(x):
        nums.pint_load_event.wait()
        if hasattr (x, "magnitude"):
            x_deg = x.to (UREG.degree)
        else:
            x_deg = x * math.pi / 180
        return f (x_deg)
    return UNARY (g)

def DEGREE_INVTRIG (f):
    """Create a unary inverse trig operator that returns degrees.

    This returns a pint object if pint is installed.
    """
    def g(x):
        if nums.pint is not None:
            return nums.UREG.Quantity (f (x), nums.UREG.radian).to (nums.UREG.degree)
        else:
            return f (x) * 180 / math.pi
    return UNARY (g)

###############################################################################
# UNIT/TAG COMMANDS

def _tag (stack, arg=None):
    """Pop a string and then a number from the stack, then create a tagged
    number."""
    tag = stack.pop ()
    num = stack.pop ()
    if not isinstance(tag, str):
        raise TypeError ("to create tagged number, expect Y: number, X: string")
    elif not isinstance(num, float) and not hasattr(num, "magnitude"):
        raise TypeError ("to create tagged number, expect Y: number, X: string ")
    stack.append (nums.Tagged (num, tag))

def _untag (stack, arg=None):
    """Pop a tagged number, then push back the original number and tag."""
    tagged = stack.pop ()
    if not isinstance(tagged, nums.Tagged):
        stack.append (tagged)
    else:
        stack.append (tagged.num)

def _convert (stack, arg=None):
    if arg is not None:
        units = nums.UREG.parse_units (arg)
        value = stack.pop ()
    else:
        units = stack.pop ().units
        value = stack.pop ()
    if isinstance (value, nums.Tagged):
        tag = value.tag
        value = value.num
    else:
        tag = None
    converted = value.to (units)
    if tag is not None:
        converted = nums.Tagged (converted, tag)
    stack.append (converted)

def GET_PREFERRED_UNITS ():
    nums.pint_load_event.wait()
    U = nums.UREG.parse_units
    PREFERRED = [
        U("V"), U("V/m"),
        U("ohm"), U("farad"), U("henry"),
        U("W"), U("J"),
        U("s"), U("Hz"), U("m"), U("g"),
        ]
    return PREFERRED

def _preferred (stack, arg):
    value = stack.pop ()
    if isinstance (value, nums.Tagged):
        tag = value.tag
        value = value.num
    else:
        tag = None

    value_base = value.to_base_units ()
    dest_unit = None

    for dest in GET_PREFERRED_UNITS():
        src = nums.UREG.Quantity(1., dest).to_base_units().units
        if src == value_base.units:
            dest_unit = dest
            break
    
    if dest_unit is None:
        converted = value
    else:
        converted = value.to (dest_unit)

    if tag is not None:
        converted = nums.Tagged (converted, tag)
    stack.append (converted)

def _list_preferred (stack, arg):

    lines = []
    for i in GET_PREFERRED_UNITS ():
        lines.append (str (i))

    scrollbox = CursesScrollBox (-4, -4)
    scrollbox.set_title ("PREFERRED UNITS")
    scrollbox.set_text (lines)
    scrollbox.show ()


################################################################################
# STACK/CLIPBOARD/SHELL COMMANDS

def _drop (stack, arg=None):
    stack.pop ()

def _dup (stack, arg=None):
    if len (stack):
        stack.append (stack[-1])

def _undo (stack, arg=None):
    # Have to run twice, because undopush was called right before this
    stack.undo ()
    stack.undo ()

def _xchg (stack, arg=None):
    a = stack.pop ()
    b = stack.pop ()
    stack.append (a)
    stack.append (b)

def _get (stack, arg=None):
    """Grab an element from the stack by index and dup it onto the end"""
    n = stack.pop ()
    if n >= 0 and n < len (stack):
        stack.append (stack [int (n)])
    else:
        stack.append (0.)

# Pyperclip is optional
try:
    import pyperclip
except ImportError:
    pyperclip = None

def _copy (stack, arg=None):
    item = stack[-1]
    if isinstance(item, str):
        fmt = item
    elif isinstance(item, float):
        fmt = str(item)

    elif isinstance(item, nums.Tagged):
        fmt = str(item.num)

    if pyperclip is not None:
        pyperclip.copy (fmt)
    else:
        xclip = subprocess.Popen (["xclip", "-selection", "CLIPBOARD"], stdin=subprocess.PIPE)
        xclip.stdin.write (fmt.encode('utf8'))
        xclip.stdin.close ()
        xclip.wait ()

def _paste (stack, arg=None):
    if pyperclip is not None:
        item = float (pyperclip.paste ())
        stack.append (item)

    else:
        clipbd = subprocess.check_output (["xclip", "-selection", "CLIPBOARD", "-o"])
        item = float(clipbd)
        stack.append (item)

import os
import re
import subprocess
def _sh (stack, arg):
    newenv = dict (os.environ)
    if not stack:
        newenv["N"] = "0"
        newenv["F"] = "0"
    else:
        num = stack[-1]
        if isinstance(num, nums.Tagged):
            num = num.num
        if isinstance(num, float):
            newenv["N"] = "%g" % num
            newenv["F"] = "%g" % num
        else:
            newenv["N"] = "%g" % num.magnitude
            newenv["F"] = "{:g~}".format (num)
    
    try:
        p = subprocess.Popen (arg, shell=True, env=newenv, stdout=subprocess.PIPE)
        data = p.stdout.read ().decode ("utf8")
        p.wait ()
    except KeyboardInterrupt:
        data = ""

    FLOAT_RE = r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?"
    match = re.search (FLOAT_RE, data)
    if match is not None:
        try:
            stack.append (float (match.group(0)))
        except ValueError as e:
            pass

    scrollbox = CursesScrollBox (-4, -4)
    scrollbox.set_title ("COMMAND OUTPUT")
    scrollbox.set_text (data)
    scrollbox.show ()

################################################################################
# DISPLAY/FORMATTING/SETTINGS/HELP COMMANDS

import string
def _help (stack, arg=None):
    """Display the command helptexts"""
    scrollbox = CursesScrollBox (-4, -4)
    scrollbox.set_title ("HELP :: up/down/pgup/pgdown; other=close")

    lines_left = []
    lines_right = []

    for key in COMMANDS.keys():
        val = COMMANDS[key]
        if isinstance(key, int):
            lines_left.append (" " * 26)
            lines_left.append ("%-26s" % val)
        else:
            lines_left.append ("%-10s %-15s" % (key, val[1]))

    for key in SINGLE_LETTER_COMMANDS.keys():
        if not isinstance (key, str):
            continue
        if key[0] not in string.digits+string.ascii_letters+string.punctuation:
            continue
        val = SINGLE_LETTER_COMMANDS[key]
        lines_right.append ("%-10s %-15s" % (key, val[1]))

    if len (lines_left) < len (lines_right):
        lines_left.extend ([""] * (len (lines_right) - len (lines_left)))
    if len (lines_left) > len (lines_right):
        lines_right.extend ([""] * (len (lines_left) - len (lines_right)))

    lines = [i + "    " + j for i,j in zip(lines_left, lines_right)]
    scrollbox.set_text (lines)

    scrollbox.show ()

import traceback
def _exc (stack, arg=None):
    """Display the latest exception"""
    if env.ERROR is None:
        return
    s = traceback.format_tb (env.ERROR[2])
    scrollbox = CursesScrollBox (-4, -4)
    scrollbox.set_title ("LAST BACKTRACE")
    scrollbox.set_text (s)
    scrollbox.show ()


def _eng (stack, arg=None):
    env.FORMAT = "eng"

    if arg is not None and arg.strip():
        env.SIGFIGS = int(arg.strip())
    else:
        env.SIGFIGS = 7

def _sci (stack, arg=None):
    env.FORMAT = "sci"

################################################################################
# ADDING SINGLE-LETTER COMMANDS
#
# Insert a compound tuple into the OrderedDict below:
# (key, (operator, helptext))
#
# key:      the key returned by curses. For printables, just the character.
# operator: a function that takes the current UndoStack, operates on it,
#               and returns nothing. Any exceptions thrown in here will be
#               caught and handled, so don't worry about those.
# helptext: a string to display on the help screen.
#
#
# Standard unary and binary operators can be made with UNARY() and BINARY(),
# which accept a lambda function taking one or two arguments and return an
# operator closure around it.

SINGLE_LETTER_COMMANDS = collections.OrderedDict([
    ("\x7f", (_drop, "drop")),
    ("\x08", (_drop, "drop")),
    (curses.KEY_BACKSPACE, (_drop, "drop")),

    ("\r", (_dup, "dup")),
    ("\n", (_dup, "dup")),
    (curses.KEY_ENTER, (_dup, "dup")),

    ("-", (BINARY (lambda x, y: x - y), "subtract")),
    ("+", (BINARY (lambda x, y: x + y), "add")),
    ("*", (BINARY (lambda x, y: x * y), "multiply")),
    ("/", (BINARY (lambda x, y: x / y), "divide")),
    ("^", (BINARY (lambda x, y: x ** y), "power")),
    ("e", (UNARY (math.exp), "exponential")),
    ("r", (UNARY (lambda x: x ** 0.5), "sq root")),
    ("i", (UNARY (lambda x: 1/x), "reciprocal")),

    ("u", (_undo, "undo")),
    ("x", (_xchg, "exchange")),
    ("[", (_get, "dup item by number")),

    ("t", (_tag, "attach tag to number")),
    ("T", (_untag, "unTag")),
    ("U", (UNARY (lambda x: x.magnitude), "unUnit")),

    ("c", (_copy, "copy to clipboard")),
    ("v", (_paste, "paste from clipboard")),

    ("?", (_help, "display help")),
])

################################################################################
# ADDING NAMED COMMANDS
#
# Insert a compound tuple into the OrderedDict below:
# (name, (operator, helptext))
#
# name:     the full command name, including beginning single-quote
# operator: a function that takes the current UndoStack, operates on it,
#               and returns nothing. Any exceptions thrown in here will be
#               caught and handled, so don't worry about those.
# helptext: a string to display on the help screen.
#
#
# Standard unary and binary operators can be made with UNARY() and BINARY(),
# which accept a lambda function taking one or two arguments and return an
# operator closure around it.
#
#
# You can insert section headers into the help text by adding a compound tuple:
# (id, header)
#
# id:       any unique integer
# header:   header text

COMMANDS = collections.OrderedDict([
    (1, "==TRIGONOMETRY, RAD=="),
    ("'sin", (UNARY (math.sin), "sin(rad)")),
    ("'cos", (UNARY (math.cos), "cos(rad)")),
    ("'tan", (UNARY (math.tan), "tan(rad)")),
    ("'asin", (UNARY (lambda x: math.asin(x) * nums.Q_("1 rad")), "asin->rad")),
    ("'acos", (UNARY (lambda x: math.acos(x) * nums.Q_("1 rad")), "acos->rad")),
    ("'atan", (UNARY (lambda x: math.atan(x) * nums.Q_("1 rad")), "atan->rad")),
    (2, "==TRIGONOMETRY, DEG=="),
    ("'sind", (DEGREE_TRIG (math.sin), "sin(deg)")),
    ("'cosd", (DEGREE_TRIG (math.cos), "cos(deg)")),
    ("'tand", (DEGREE_TRIG (math.tan), "tan(deg)")),
    ("'asind", (DEGREE_INVTRIG (math.asin), "asin->deg")),
    ("'acosd", (DEGREE_INVTRIG (math.acos), "acos->deg")),
    ("'atand", (DEGREE_INVTRIG (math.atan), "atan->deg")),
    ("'deg", (UNARY (math.degrees), "rad->deg")),
    ("'rad", (UNARY (math.radians), "deg->rad")),
    (3, "==HYPERBOLICS=="),
    ("'sinh", (UNARY (math.sinh), "sinh")),
    ("'cosh", (UNARY (math.cosh), "cosh")),
    ("'tanh", (UNARY (math.tanh), "tanh")),
    ("'asinh", (UNARY (math.asinh), "asinh")),
    ("'acosh", (UNARY (math.acosh), "acosh")),
    ("'atanh", (UNARY (math.atanh), "atanh")),
    (4, "==LOGARITHMS=="),
    ("'log", (UNARY (math.log), "log base e")),
    ("'log10", (UNARY (math.log10), "log base 10")),
    ("'log2", (UNARY (math.log2), "log base 2")),
    (7, "==UNITS=="),
    ("'mag", (UNARY (lambda x: x.magnitude), "return magnitude without unit")),
    ("'unity", (UNARY (lambda x: nums.UREG.Quantity(1., x.units)), "return 1.0*unit")),
    ("'base", (UNARY (lambda x: x.to_base_units()), "convert to base units")),
    ("'pu", (_preferred, "convert to preferred units")),
    ("'pu?", (_list_preferred, "show the list of preferred units")),
    ("'conv", (_convert, "convert Y to units of X, or X to units of command argument")),
    (5, "==CONSTANTS=="),
    ("'pi", (lambda stack,a=None: stack.append (math.pi), "const PI")),
    ("'e", (lambda stack,a=None: stack.append (math.e), "const E")),
    ("'c", (lambda stack,a=None: stack.append (nums.Q_("2.99792458e8 m/s")), "speed of light, m/s")),
    ("'h", (lambda stack,a=None: stack.append (nums.Q_("6.6260755e-34 J S")), "Planck constant, J s")),
    ("'k", (lambda stack,a=None: stack.append (nums.Q_("1.380658e-23 J/K")), "Boltzmann constant, J/K")),
    ("'elec", (lambda stack,a=None: stack.append (nums.Q_("1.60217733e-19 C")), "Charge of electron, C")),
    ("'e0", (lambda stack,a=None: stack.append (nums.Q_("8.854187817e-12 F/m")), "Permittivity of vacuum, F/m")),
    ("'amu", (lambda stack,a=None: stack.append (nums.Q_("1.6605402e-27 kg")), "Atomic mass unit, kg")),
    ("'Na", (lambda stack,a=None: stack.append (nums.Q_("6.0221367e23 1/mol")), "Avogadro's number, mol^-1")),
    ("'atm", (lambda stack,a=None: stack.append (nums.Q_("101325. Pa")), "Standard atmosphere, Pa")),
    (6, "==LERPN=="),
    ("'sh", (_sh, "run shell command, $N = magnitude, $F = full number with unit")),
    ("'help", (_help, "display help")),
    ("'exc", (_exc, "display latest exception backtrace")),
    ("'eng", (_eng, "engineering mode, sig figs = 7 or command argument")),
    ("'sci", (_sci, "scientific mode")),
])
