"""Code dealing with numbers.
"""

import re
import math

FLOAT_RE = re.compile(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
FLOAT_RE_UNDER = re.compile(r"[-_+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")

# Hack warning!
# Pint takes too long to load for a general-purpose calculator that has to come
# up quickly. Since it's not needed until after the first line has been
# entered, I'm throwing up a loader in a thread. Blame nickjohnson if it's bad
import threading
pint = None     # pylint: disable=invalid-name
PINT_LOAD_EVENT = threading.Event()
UREG = None
def pintloader():
    """Thread that attempts to load pint in the background.
    """
    # pylint: disable=redefined-outer-name,invalid-name,global-statement

    global pint, UREG
    try:
        import pint
        UREG = pint.UnitRegistry()
        UREG.autoconvert_offset_to_baseunit = True
        PINT_LOAD_EVENT.set()
    except ImportError:
        pint = None
        PINT_LOAD_EVENT.set()

PINT_LOADER = threading.Thread(target=pintloader)
PINT_LOADER.start()

NUM_PARSE_RE = re.compile(
    r"\s*(?P<re>" + FLOAT_RE_UNDER.pattern + r")" +     # real part
    r"\s*(?P<im>[jJ]\s*" + FLOAT_RE_UNDER.pattern + ")?" + # imaginary part
    r'\s*(?P<unit>[^\s"]+)?' +                          # unit
    r'\s*(?P<tag>".*)?' +                               # tag
    "$")

def num_parser(in_str):
    """Parse a number from user input.

    This accepts any combination of real part, imaginary part, unit, and tag.

    1.2e3   j5.4e-8    m/s^2    " complex acceleration!
    """

    PINT_LOAD_EVENT.wait()

    match = NUM_PARSE_RE.match(in_str)

    if match is None:
        raise ValueError("Cannot parse value %r" % in_str)

    real_str = match.group("re")
    if real_str.startswith("_"):
        real_str = "-" + real_str[1:]
    real = float(real_str)

    if match.group("im") is not None:
        imag_str = match.group("im")[1:].strip()
        if imag_str.startswith("_"):
            imag_str = "-" + imag_str[1:]
        imag = float(imag_str)
    else:
        imag = None

    if imag is None:
        value = real
    else:
        value = complex(real, imag)

    if match.group("unit") is not None:
        unit = UREG.parse_units(match.group("unit"))
        value = UREG.Quantity(value, unit)

    if match.group("tag") is not None:
        value = Tagged(value, match.group("tag")[1:].strip())

    return value

def Q_(in_str):
    # pylint: disable=invalid-name
    """Parse an expression with unit to a number.

    This is generally for use in code (constants, etc), not for interpreting
    user input. It waits to see whether pint will load - if it does, it passes
    the expression to pint; if not, it strips off the unit and parses the rest
    with float().
    """

    PINT_LOAD_EVENT.wait()
    if UREG is None:
        return float(in_str.partition(" ")[0])
    else:
        return UREG.parse_expression(in_str)

class UndoStack(list):
    """Stack supporting an 'undo' action.
    This is used as the main RPN stack. You can append() and pop() and [] just
    like with a normal list. You can also use undopush() to push a duplicate of
    the stack itself onto a "stack of stacks", and then undo() to restore that.
    """

    def __init__(self, v=None):
        """Initialize an UndoStack from an optional source list.
        """
        if v is None:
            list.__init__(self)
            self.__sos = [[]]

        else:
            list.__init__(self, v)
            self.__sos = [[]]

        self.parent = None

    def undopush(self):
        """Save the current stack state to be restored later with undo()
        """
        self.__sos.append(self[:])

    def undo(self):
        """Restore the last saved undo state
        """
        if len(self.__sos) > 1:
            self[:] = self.__sos.pop()
        else:
            self[:] = []

    def __str__(self):
        return "<< STACK(%d) >>" % len(self)

    def __add__(self, other):
        if isinstance(other, UndoStack):
            assert self.parent is other.parent
            new_stack = UndoStack(list.__add__(self, other))
            new_stack.parent = self.parent
            return new_stack
        else:
            return self.__add_real__(other) # pylint: disable=no-member

    def __radd__(self, other):
        # pylint: disable=no-member
        return self.__radd_real__(other)

    @classmethod
    def generate_operators(cls):
        """Autogenerates a set of operator overloads"""
        # Add operations to Tagged
        ops = [
            ("add_real", lambda x, y: x+y),
            ("sub", lambda x, y: x-y),
            ("mul", lambda x, y: x*y),
            ("truediv", lambda x, y: x/y),
            ("mod", lambda x, y: x%y),
            ("pow", lambda x, y: x**y),
            ]
        for opname, opfunc in ops:
            def method(self, other, opfunc=opfunc):
                if not isinstance(other, float) and not isinstance(other, complex):
                    return NotImplemented
                new_stack = cls(opfunc(i, other) for i in self)
                new_stack.parent = self.parent
                return new_stack

            def rmethod(self, other, opfunc=opfunc):
                if not isinstance(other, float) and not isinstance(other, complex):
                    return NotImplemented
                new_stack = cls(opfunc(other, i) for i in self)
                new_stack.parent = self.parent
                return new_stack

            setattr(cls, "__%s__" % opname, method)
            setattr(cls, "__r%s__" % opname, rmethod)

UndoStack.generate_operators()

class Tagged(object):
    """Tagged number object.
    This behaves like a number, but also contains a string tag. The values
    are accessible at .num and .tag
    """
    def __init__(self, num, tag):
        assert isinstance(tag, str)
        self._num = num
        self._tag = tag

    @property
    def num(self):
        """the number that is tagged"""
        return self._num

    @property
    def tag(self):
        """the tag applied to the number"""
        return self._tag

    @classmethod
    def generate_operators(cls):
        """Autogenerates a set of operator overloads"""
        # Add operations to Tagged
        ops = [
            ("add", lambda x, y: x+y),
            ("sub", lambda x, y: x-y),
            ("mul", lambda x, y: x*y),
            ("truediv", lambda x, y: x/y),
            ("mod", lambda x, y: x%y),
            ("pow", lambda x, y: x**y),
            ]
        for opname, opfunc in ops:
            # For the uninitiated, the default-argument parameters create a new
            # scope for the variable, allowing passing each loop iteration's value
            # to the closure instead of closing around the single final value.
            def method(self, other, opfunc=opfunc):
                if isinstance(other, cls):
                    # If both are tagged, just remove the tag.
                    return opfunc(self.num, other.num)
                if not isinstance(other, float) and not isinstance(other, complex):
                    return NotImplemented
                return cls(opfunc(self.num, other), self.tag)

            def rmethod(self, other, opfunc=opfunc):
                if isinstance(other, cls):
                    # If both are tagged, just remove the tag.
                    return opfunc(other.num, self.num)
                if not isinstance(other, float) and not isinstance(other, complex):
                    return NotImplemented
                return cls(opfunc(other, self.num), self.tag)

            setattr(cls, "__%s__" % opname, method)
            setattr(cls, "__r%s__" % opname, rmethod)

Tagged.generate_operators()

LUT = {
    -24: "y",
    -21: "z",
    -18: "a",
    -15: "f",
    -12: "p",
    -9: "n",
    -6: u"\xb5",
    -3: "m",
    0: "",
    3: "k",
    6: "M",
    9: "G",
    12: "T",
    15: "P",
    18: "E",
    21: "Z",
    24: "Y"
}
def eng(num, sigfigs=7):
    """Return num in engineering notation"""

    if isinstance(num, complex):
        real = num.real
        imag = num.imag
        imag_sign = "+" if imag >= 0.0 else "-"
        imag_abs = abs(imag)

        return "(%s %sj %s)" %(eng(real), imag_sign, eng(imag_abs))

    if num == 0.0:
        return "0"

    elif num < 0.0:
        return '-'+eng(-num, sigfigs)

    magnitude = math.floor(math.log10(num)/3)*3
    coeff = "{0:.{1}g}".format(num * 10.0 ** (-magnitude), sigfigs)
    lut = LUT.get(magnitude, None)
    if lut is None:
        return coeff + "e" + str(magnitude)
    if lut != '':
        lut = '_' + lut
    return coeff + lut

class DisplayMode(object):
    @classmethod
    def format_real(cls, num):
        raise NotImplementedError

    @classmethod
    def format(cls, num):
        """Format the number in the subclass mode. Do not call this directly
        on DisplayMode, only on its subclasses."""
        if isinstance(num, Tagged):
            return cls.format(num.num)

        elif hasattr(num, "magnitude"):
            one_magnitude_unit = format(UREG.Quantity(1, num.units), "~")
            assert one_magnitude_unit.startswith("1 ")
            units_abbrev = one_magnitude_unit[2:]

            return "%s %s" % (cls.format(num.magnitude), units_abbrev)

        elif isinstance(num, float):
            return cls.format_real(num)

        elif isinstance(num, complex):
            real = num.real
            imag = num.imag
            imag_sign = "+" if imag >= 0.0 else "-"
            imag_abs = abs(imag)

            return "(%s %sj %s)" % (cls.format_real(real), imag_sign, cls.format_real(imag_abs))

        elif isinstance(num, str):
            return repr(num)

        else:
            return str(num)

class EngMode(DisplayMode):
    sigfigs = 7
    @classmethod
    def format_real(cls, num):
        """Format a float in engineering mode"""
        return eng(num, cls.sigfigs)

class FixMode(DisplayMode):
    digits = 6
    @classmethod
    def format_real(cls, num):
        """Format a float in fixed mode"""
        return "%.*f" % (cls.digits, num)

class NaturalMode(DisplayMode):
    @classmethod
    def format_real(cls, num):
        """Format a float in natural mode"""
        return "%g" % num

class SciMode(DisplayMode):
    @classmethod
    def format_real(cls, num):
        """Format a float in scientific mode"""
        return "%e" % num
