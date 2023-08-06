"""All the calculator commands.

This file contains the commands made available to the user. Single-key
commands are in the SINGLE_KEY_COMMANDS OrderedDict, and full-name
commands are in the COMMANDS OrderedDict.
"""

import collections
import curses
import math
import cmath

from . import nums, env, curses_stuff

###############################################################################
# COMMAND GENERATORS
#
# Use these to generate common cases, rather than implementing from scratch.

def BINARY(func, docstring=None):
    """Create a binary operator from a lambda function."""
    def cmd(stack, arg):
        assert not arg, "no argument expected!"
        y_val = stack.pop()
        x_val = stack.pop()
        stack.append(func(x_val, y_val))
    if docstring is not None:
        cmd.__doc__ = docstring
    else:
        cmd.__doc__ = func.__doc__
    assert cmd.__doc__
    return cmd

def UNARY(func, docstring=None):
    """Create a unary operator from a lambda function.
    The unary operators know how to handle tagged numbers - they reapply the
    same tag after performing the operation."""
    def cmd(stack, arg):
        assert not arg, "no argument expected!"
        value = stack.pop()
        if isinstance(value, nums.Tagged):
            newtagged = nums.Tagged(func(value.num), value.tag)
            stack.append(newtagged)
        else:
            stack.append(func(value))
    if docstring is not None and docstring:
        cmd.__doc__ = docstring
    else:
        cmd.__doc__ = func.__doc__
    assert cmd.__doc__
    return cmd

def DEGREE_TRIG(func):
    """Create a unary trig operator that accepts degrees.

    This has to be handled specially because pint supports degrees/radians,
    performing the conversion automatically. We have to avoid double-converting,
    and also work in the absence of pint.
    """
    def degree_trig(value):
        nums.PINT_LOAD_EVENT.wait()
        if hasattr(value, "magnitude"):
            value_deg = value.to(nums.UREG.degree)
        else:
            value_deg = value * math.pi / 180
        return func(value_deg)
    return degree_trig

def DEGREE_INVTRIG(func):
    """Create a unary inverse trig operator that returns degrees.

    The operator returns a pint object if pint is installed.
    """
    def degree_invtrig(value):
        if nums.pint is not None:
            return nums.UREG.Quantity(func(value), nums.UREG.radian).to(nums.UREG.degree)
        else:
            return func(value) * 180 / math.pi
    return degree_invtrig

def AUTOC(fname):
    """Return a wrapper function that calls Call math.<fname> for floats and
    ints, cmath.<fname> for complex"""

    def autoc(n, *args):
        if isinstance(n, complex):
            return getattr(cmath, fname)(n, *args)
        else:
            return getattr(math, fname)(n, *args)
    return autoc

def CONST(val, descr):
    """Return a command function to push a constant"""

    if isinstance(val, str):
        def cmd(stack, arg):
            assert not arg, "no argument expected!"
            stack.append(nums.Q_(val))
    else:
        def cmd(stack, arg):
            assert not arg, "no argument expected!"
            stack.append(val)
    cmd.__doc__ = descr
    return cmd

###############################################################################
# MATH COMMANDS

@UNARY
def _to_deg(value):
    """rad->deg"""
    if hasattr(value, "to"):
        return value.to(nums.UREG.parse_units("deg"))
    else:
        return value * 180 / math.pi

@UNARY
def _to_rad(value):
    """deg->rad"""
    if hasattr(value, "to"):
        return value.to(nums.UREG.parse_units("rad"))
    else:
        return value * math.pi / 180

def _reim(stack, arg):
    """split into real and imaginary parts"""
    assert not arg, "no argument expected!"
    num = stack.pop()
    if isinstance(num, nums.Tagged):
        num = num.num
    real = num.real
    imag = num.imag
    stack.append(real)
    stack.append(imag)

def _polar(stack, arg):
    """split into absolute value and angle"""
    assert not arg, "no argument expected!"
    num = stack.pop()
    if isinstance(num, nums.Tagged):
        num = num.num

    if hasattr(num, "units"):
        units = num.units
        num = num.magnitude
    else:
        units = None

    absval = abs(num)
    angle = cmath.phase(num) * nums.Q_("1 rad")

    if units is not None:
        absval = nums.UREG.Quantity(absval, units)

    stack.append(absval)
    stack.append(angle)

def _fromcart(stack, arg):
    """make complex from Cartesian real, imag"""
    assert not arg, "no argument expected!"
    imag = stack.pop()
    real = stack.pop()

    if isinstance(imag, nums.Tagged):
        imag = imag.num
    if isinstance(real, nums.Tagged):
        real = real.num

    # We can handle units here. Attempt to mash the second into the first,
    # let it error out if not possible
    if hasattr(imag, "to"):
        im_converted = imag.to(real.units)
        imag = im_converted.magnitude
        units = real.units
        real = real.magnitude
    else:
        units = None

    cval = complex(real, imag)

    if units is not None:
        cval = nums.UREG.Quantity(cval, units)

    stack.append(cval)

def _frompolar(stack, arg):
    """make complex from polar abs val, angle(assume rad if no unit support)"""
    assert not arg, "no argument expected!"
    angle = stack.pop()
    absval = stack.pop()

    if isinstance(angle, nums.Tagged):
        angle = angle.num
    if isinstance(absval, nums.Tagged):
        absval = absval.num

    # Angle must be in radians
    if hasattr(angle, "to"):
        angle = angle.to("rad")

    # Save unit from absval
    if hasattr(absval, "units"):
        units = absval.units
        absval = absval.magnitude
    else:
        units = None

    cval = cmath.rect(absval, angle)

    if units is not None:
        cval = nums.UREG.Quantity(cval, units)

    stack.append(cval)

def _pvar(stack, arg):
    """population variance"""
    assert not arg, "no argument expected!"
    nest = stack.pop()
    mean = sum(nest) / float(len(nest))
    sdiff = [(i - mean) ** 2 for i in nest]
    pvar = sum(sdiff) / float(len(sdiff))
    stack.append(pvar)

def _pdev(stack, arg):
    """population std deviation"""
    _pvar(stack, arg)
    stack.append(stack.pop() ** 0.5)

def _svar(stack, arg):
    """sample variance"""
    assert not arg, "no argument expected!"
    nest = stack.pop()
    mean = sum(nest) / float(len(nest))
    sdiff = [(i - mean) ** 2 for i in nest]
    svar = sum(sdiff) / float(len(sdiff) - 1)
    stack.append(svar)

def _sdev(stack, arg):
    """sample std deviation"""
    _svar(stack, arg)
    stack.append(stack.pop() ** 0.5)

###############################################################################
# UNIT/TAG COMMANDS

def _tag(stack, arg):
    """attach tag to number"""

    if arg:
        tag = arg.strip()
    else:
        tag = stack.pop()

    num = stack.pop()
    if not isinstance(tag, str):
        raise TypeError("to create tagged number, expect Y: number, X: string")

    elif (not isinstance(num, float) and
          not hasattr(num, "magnitude") and not isinstance(num, nums.UndoStack)):
        raise TypeError("to create tagged number, expect Y: number, X: string ")

    stack.append(nums.Tagged(num, tag))

def _untag(stack, arg):
    """unTag"""
    assert not arg, "no argument expected!"
    tagged = stack.pop()
    if not isinstance(tagged, nums.Tagged):
        stack.append(tagged)
    else:
        stack.append(tagged.num)

def _convert(stack, arg):
    """convert Y to units of X, or X to units of command argument"""
    if arg is not None:
        units = nums.UREG.parse_units(arg)
        value = stack.pop()
    else:
        units = stack.pop().units
        value = stack.pop()
    if isinstance(value, nums.Tagged):
        tag = value.tag
        value = value.num
    else:
        tag = None
    converted = value.to(units)
    if tag is not None:
        converted = nums.Tagged(converted, tag)
    stack.append(converted)

def get_preferred_units():
    """Return a list of preferred Pint units, after Pint has loaded."""
    nums.PINT_LOAD_EVENT.wait()
    preferred_names = [
        "V", "V/m",
        "siemens", "weber", "tesla", "ohm", "farad", "henry",
        "W", "J",
        "s", "Hz", "m", "g",
        "liter",
        ]
    preferred_units = [nums.UREG.parse_units(i) for i in preferred_names]
    return preferred_units

def _preferred(stack, arg):
    """convert to preferred units"""
    assert not arg, "no argument expected!"
    value = stack.pop()
    if isinstance(value, nums.Tagged):
        tag = value.tag
        value = value.num
    else:
        tag = None

    value_base = value.to_base_units()
    dest_unit = None

    for dest in get_preferred_units():
        src = nums.UREG.Quantity(1., dest).to_base_units().units
        if src == value_base.units:
            dest_unit = dest
            break

    if dest_unit is None:
        converted = value
    else:
        converted = value.to(dest_unit)

    if tag is not None:
        converted = nums.Tagged(converted, tag)
    stack.append(converted)

def _list_preferred(stack, arg):
    """show the list of preferred units"""
    assert not arg, "no argument expected!"
    lines = []
    for i in get_preferred_units():
        lines.append(str(i))

    scrollbox = curses_stuff.CursesScrollBox(-4, -4)
    scrollbox.set_title("PREFERRED UNITS")
    scrollbox.set_text(lines)
    scrollbox.show()


################################################################################
# STACK/CLIPBOARD/SHELL COMMANDS

def _drop(stack, arg):
    """drop"""
    assert not arg, "no argument expected!"
    stack.pop()

def _dup(stack, arg):
    """dup"""
    assert not arg, "no argument expected!"
    # pop instead of access so we get the same, consistent error message if
    # there isn't one.
    item = stack.pop()
    stack.append(item)
    if isinstance(item, nums.UndoStack):
        new_item = nums.UndoStack(item)
        new_item.parent = stack
    elif isinstance(item, nums.Tagged) and isinstance(item.num, nums.UndoStack):
        new_stack = nums.UndoStack(item.num)
        new_stack.parent = stack
        new_item = nums.Tagged(new_stack, item.tag)
    else:
        new_item = item
    stack.append(new_item)

def _rotup(stack, arg):
    """rotate up"""
    assert not arg, "no argument expected!"
    stack.append(stack.pop(0))

def _rotdown(stack, arg):
    """rotate down"""
    assert not arg, "no argument expected!"
    stack.insert(0, stack.pop(-1))

def _pull(stack, arg):
    """move item from index to front"""
    assert not arg, "no argument expected!"
    idx = int(stack.pop())
    stack.append(stack.pop(idx))

def _push(stack, arg):
    """move item from front to index"""
    assert not arg, "no argument expected!"
    idx = int(stack.pop())
    stack.insert(idx, stack.pop())

def _undo(stack, arg):
    """undo"""
    assert not arg, "no argument expected!"
    # Have to run twice, because undopush was called right before this
    stack.undo()
    stack.undo()

def _xchg(stack, arg):
    """exchange/swap"""
    assert not arg, "no argument expected!"
    val_a = stack.pop()
    val_b = stack.pop()
    stack.append(val_a)
    stack.append(val_b)

def _get(stack, arg):
    """dup item by number"""
    assert not arg, "no argument expected!"
    stack_idx = int(stack.pop())
    if stack_idx >= 0 and stack_idx < len(stack):
        item = stack[stack_idx]
    else:
        item = 0.
    if isinstance(item, nums.UndoStack):
        new_item = nums.UndoStack(item)
        new_item.parent = stack
    else:
        new_item = item
    stack.append(new_item)


# Pyperclip is optional
try:
    import pyperclip
except ImportError:
    pyperclip = None

def _copy(stack, arg):
    """copy to clipboard"""
    assert not arg, "no argument expected!"
    item = stack[-1]
    if isinstance(item, str):
        fmt = item
    elif isinstance(item, float) or isinstance(item, complex):
        fmt = str(item)

    elif isinstance(item, nums.Tagged):
        fmt = str(item.num)

    if pyperclip is not None:
        pyperclip.copy(fmt)
    else:
        xclip = subprocess.Popen(["xclip", "-selection", "CLIPBOARD"], stdin=subprocess.PIPE)
        xclip.stdin.write(fmt.encode('utf8'))
        xclip.stdin.close()
        xclip.wait()

def _paste(stack, arg):
    """paste from clipboard"""
    assert not arg, "no argument expected!"
    if pyperclip is not None:
        item = float(pyperclip.paste())
        stack.append(item)

    else:
        clipbd = subprocess.check_output(["xclip", "-selection", "CLIPBOARD", "-o"])
        item = float(clipbd)
        stack.append(item)

import os
import subprocess
def _sh(stack, arg):
    """run shell command, $N = magnitude, $F = full number with unit"""
    assert arg, "argument expected!"
    newenv = dict(os.environ)
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
        elif isinstance(num, complex):
            newenv["N"] = "%g+%gj" %(num.real, num.imag)
            newenv["F"] = "%g+%gj" %(num.real, num.imag)
        elif hasattr(num, "magnitude") and isinstance(num.magnitude, float):
            newenv["N"] = "%g" % num.magnitude
            newenv["F"] = "{:g~}".format(num)
        elif hasattr(num, "magnitude") and isinstance(num.magnitude, complex):
            newenv["N"] = "%g+%gj" %(num.magnitude.real, num.magnitude.imag)
            newenv["F"] = "{:g~}".format(num)

    try:
        proc = subprocess.Popen(
            arg, shell=True, env=newenv, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        data = proc.stdout.read().decode("utf8")
        proc.wait()
    except KeyboardInterrupt:
        data = ""

    match = nums.FLOAT_RE.search(data)
    if match is not None:
        try:
            stack.append(float(match.group(0)))
        except ValueError:
            pass

    scrollbox = curses_stuff.CursesScrollBox(-4, -4)
    scrollbox.set_title("COMMAND OUTPUT")
    scrollbox.set_text(data)
    scrollbox.show()

def _newstack(stack, arg):
    """push a new nested stack"""
    assert not arg, "no argument expected!"
    new_stack = nums.UndoStack()
    new_stack.parent = stack
    stack.append(new_stack)
    env.STACK = new_stack

def _enterstack(stack, arg):
    """enter a nested stack"""
    assert not arg, "no argument expected!"
    child = stack[-1]
    if isinstance(child, nums.Tagged):
        child = child.num
    if not isinstance(child, nums.UndoStack):
        raise TypeError("can only enter a nested stack, not a value")
    env.STACK = child

    # Remove extra undo item
    stack.undo()

def _leavestack(stack, arg):
    """return to the parent stack"""
    assert not arg, "no argument expected!"
    if stack.parent is None:
        raise Exception("cannot move above the root stack")
    env.STACK = stack.parent

    # Remove extra undo item
    stack.undo()

def _merge(stack, arg):
    """merge a nested stack into this stack"""
    assert not arg, "no argument expected!"
    nested = stack.pop()
    if not isinstance(nested, nums.UndoStack):
        raise TypeError("can only merge stack, not value")
    for i in nested:
        if isinstance(i, nums.UndoStack):
            new_i = nums.UndoStack(i)
            new_i.parent = stack
            stack.append(new_i)
        else:
            stack.append(i)

def _flatten(stack, arg):
    """flatten the current stack"""

    def flatten_recursive(items, target):
        for i in items:
            if isinstance(i, nums.UndoStack):
                flatten_recursive(i, target)
            else:
                target.append(i)

    items = stack[:]
    del stack[:]
    flatten_recursive(items, stack)



################################################################################
# DISPLAY/FORMATTING/SETTINGS/HELP COMMANDS

def _help(stack, arg):
    """display help"""
    assert not arg, "no argument expected!"
    scrollbox = curses_stuff.CursesScrollBox(-4, -4)
    scrollbox.set_title("HELP")

    lines_left = []
    lines_right = []

    for key in COMMANDS.keys():
        val = COMMANDS[key]
        if isinstance(key, int):
            lines_left.append(" " * 26)
            lines_left.append("%-26s" % val)
        else:
            lines_left.append("%-10s %-15s" % (key, val.__doc__.partition("\n")[0]))

    for key in SINGLE_KEY_COMMANDS.keys():
        key_name = curses_stuff.KEY_TO_NAME.get(key, key)
        val = SINGLE_KEY_COMMANDS[key]
        lines_right.append("%-10s %-15s" % (key_name, val.__doc__.partition("\n")[0]))

    if len(lines_left) < len(lines_right):
        lines_left.extend([""] * (len(lines_right) - len(lines_left)))
    if len(lines_left) > len(lines_right):
        lines_right.extend([""] * (len(lines_left) - len(lines_right)))

    lines = [i + "    " + j for i, j in zip(lines_left, lines_right)]
    scrollbox.set_text(lines)

    scrollbox.show()

import traceback
def _exc(stack, arg):
    """display the latest exception"""
    assert not arg, "no argument expected!"
    if env.ERROR is None:
        return
    last_bt = traceback.format_tb(env.ERROR[2])
    scrollbox = curses_stuff.CursesScrollBox(-4, -4)
    scrollbox.set_title("LAST BACKTRACE")
    scrollbox.set_text(last_bt)
    scrollbox.show()

def _natural(stack, arg):
    """natural mode"""
    assert not arg, "no argument expected!"
    env.FORMAT = nums.NaturalMode

def _fix(stack, arg):
    """fixed mode, digits = 6 or command argument"""
    env.FORMAT = nums.FixMode

    if arg is not None and arg.strip():
        nums.FixMode.digits = int(arg.strip())
    else:
        nums.FixMode.digits = 6

def _eng(stack, arg):
    """engineering mode, sig figs = 7 or command argument"""
    env.FORMAT = nums.EngMode

    if arg is not None and arg.strip():
        nums.EngMode.sigfigs = int(arg.strip())
    else:
        nums.EngMode.sigfigs = 7

def _sci(stack, arg):
    """scientific mode"""
    assert not arg, "no argument expected!"
    env.FORMAT = nums.SciMode

################################################################################
# ADDING SINGLE-LETTER COMMANDS
#
# Insert a tuple into the OrderedDict below:
# (key, command)
#
# key:      the key returned by curses. For printables, just the character.
# command:  a function that takes the current UndoStack, operates on it,
#               and returns nothing. Any exceptions thrown in here will be
#               caught and handled, so don't worry about those.
#
# The command must have a docstring. The first line of this will be used as its
# help text.
#
# Standard unary and binary operators can be made with UNARY() and BINARY(),
# which accept a lambda function taking one or two arguments and return an
# operator closure around it. These take the desired docstring as the second
# argument.

SINGLE_KEY_COMMANDS = collections.OrderedDict([
    ("\x7f", _drop),
    ("\x08", _drop),
    (curses.KEY_BACKSPACE, _drop),

    ("\r", _dup),
    ("\n", _dup),
    (curses.KEY_ENTER, _dup),

    (curses.KEY_UP, _rotup),
    (curses.KEY_DOWN, _rotdown),

    ("-", BINARY(lambda x, y: x - y, "subtract")),
    ("+", BINARY(lambda x, y: x + y, "add")),
    ("*", BINARY(lambda x, y: x * y, "multiply")),
    ("/", BINARY(lambda x, y: x / y, "divide")),
    ("%", BINARY(lambda x, y: x % y, "modulo")),
    ("^", BINARY(lambda x, y: x ** y, "power")),
    ("e", UNARY(AUTOC("exp"), "exponential")),
    ("r", UNARY(lambda x: x ** 0.5, "sq root")),
    ("i", UNARY(lambda x: 1/x, "reciprocal")),

    ("u", _undo),
    ("x", _xchg),
    ("[", _get),
    ("{", _pull),
    ("}", _push),

    ("t", _tag),
    ("T", _untag),
    ("U", UNARY(lambda x: x.magnitude, "unUnit")),

    ("c", _copy),
    ("v", _paste),

    ("S", _newstack),
    (">", _enterstack),
    ("<", _leavestack),

    ("?", _help),
])

################################################################################
# ADDING NAMED COMMANDS
#
# Insert a tuple into the OrderedDict below:
# (key, command)
#
# name:     the full command name, including beginning single-quote
# command:  a function that takes the current UndoStack, operates on it,
#               and returns nothing. Any exceptions thrown in here will be
#               caught and handled, so don't worry about those.
#
# The command must have a docstring. The first line of this will be used as its
# help text.
#
# Standard unary and binary operators can be made with UNARY() and BINARY(),
# which accept a lambda function taking one or two arguments and return an
# operator closure around it. These take the desired docstring as the second
# argument.
#
# You can insert section headers into the help text by adding a tuple:
# (id, header)
#
# id:       any unique integer
# header:   header text

COMMANDS = collections.OrderedDict([
    (1, "==TRIGONOMETRY, RAD=="),
    ("'sin", UNARY(AUTOC("sin"), "sin(rad)")),
    ("'cos", UNARY(AUTOC("cos"), "cos(rad)")),
    ("'tan", UNARY(AUTOC("tan"), "tan(rad)")),
    ("'asin", UNARY(lambda x: AUTOC("asin")(x) * nums.Q_("1 rad"), "asin->rad")),
    ("'acos", UNARY(lambda x: AUTOC("acos")(x) * nums.Q_("1 rad"), "acos->rad")),
    ("'atan", UNARY(lambda x: AUTOC("atan")(x) * nums.Q_("1 rad"), "atan->rad")),
    (2, "==TRIGONOMETRY, DEG=="),
    ("'sind", UNARY(DEGREE_TRIG(AUTOC("sin")), "sin(deg)")),
    ("'cosd", UNARY(DEGREE_TRIG(AUTOC("cos")), "cos(deg)")),
    ("'tand", UNARY(DEGREE_TRIG(AUTOC("tan")), "tan(deg)")),
    ("'asind", UNARY(DEGREE_INVTRIG(AUTOC("asin")), "asin->deg")),
    ("'acosd", UNARY(DEGREE_INVTRIG(AUTOC("acos")), "acos->deg")),
    ("'atand", UNARY(DEGREE_INVTRIG(AUTOC("atan")), "atan->deg")),
    ("'deg", _to_deg),
    ("'rad", _to_rad),
    (3, "==HYPERBOLICS=="),
    ("'sinh", UNARY(AUTOC("sinh"), "sinh")),
    ("'cosh", UNARY(AUTOC("cosh"), "cosh")),
    ("'tanh", UNARY(AUTOC("tanh"), "tanh")),
    ("'asinh", UNARY(AUTOC("asinh"), "asinh")),
    ("'acosh", UNARY(AUTOC("acosh"), "acosh")),
    ("'atanh", UNARY(AUTOC("atanh"), "atanh")),
    (4, "==LOGARITHMS=="),
    ("'log", UNARY(AUTOC("log"), "log base e")),
    ("'log10", UNARY(AUTOC("log10"), "log base 10")),
    ("'log2", UNARY(lambda x: AUTOC("log")(x, 2), "log base 2")),
    (8, "==COMPLEX=="),
    ("'re", UNARY(lambda x: x.real, "real part")),
    ("'im", UNARY(lambda x: x.imag, "imaginary part")),
    ("'conj", UNARY(lambda x: complex(x.real, -x.imag), "complex conjugate")),
    ("'reim", _reim),
    ("'abs", UNARY(abs, "absolute value")),
    ("'angle", UNARY(lambda x: cmath.phase(x) * nums.Q_("1 rad"), "angle/phase (rad)")),
    ("'polar", _polar),
    ("'fcart", _fromcart),
    ("'fpolar", _frompolar),
    (7, "==UNITS=="),
    ("'mag", UNARY(lambda x: x.magnitude, "return magnitude without unit")),
    ("'unity", UNARY(lambda x: nums.UREG.Quantity(1., x.units), "return 1.0*unit")),
    ("'base", UNARY(lambda x: x.to_base_units(), "convert to base units")),
    ("'pu", _preferred),
    ("'pu?", _list_preferred),
    ("'conv", _convert),
    (9, "==NESTED STACKS=="),
    ("'sum", UNARY(sum, "sum of stack")),
    ("'mean", UNARY(lambda x: sum(x) / float(len(x)), "mean of stack")),
    ("'rms", UNARY(lambda x: (sum(i**2 for i in x) / float(len(x)))**0.5, "quadratic mean of stack")),
    ("'pvar", _pvar),
    ("'pdev", _pdev),
    ("'svar", _svar),
    ("'sdev", _sdev),
    ("'merge", _merge),
    ("'flatten", _flatten),
    (5, "==CONSTANTS=="),
    ("'pi", CONST(math.pi, "const PI")),
    ("'e", CONST(math.e, "const E")),
    ("'j", CONST(0+1j, "imaginary unit")),
    ("'c", CONST("2.99792458e8 m/s", "speed of light, m/s")),
    ("'h", CONST("6.6260755e-34 J S", "Planck constant, J s")),
    ("'k", CONST("1.380658e-23 J/K", "Boltzmann constant, J/K")),
    ("'elec", CONST("1.60217733e-19 C", "Charge of electron, C")),
    ("'e0", CONST("8.854187817e-12 F/m", "Permittivity of vacuum, F/m")),
    ("'amu", CONST("1.6605402e-27 kg", "Atomic mass unit, kg")),
    ("'Na", CONST("6.0221367e23 1/mol", "Avogadro's number, mol^-1")),
    ("'atm", CONST("101325. Pa", "Standard atmosphere, Pa")),
    (6, "==LERPN=="),
    ("'sh", _sh),
    ("'help", _help),
    ("'exc", _exc),
    ("'eng", _eng),
    ("'sci", _sci),
    ("'fix", _fix),
    ("'natural", _natural),
])
