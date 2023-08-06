import math

# Hack warning!
# Pint takes too long to load for a general-purpose calculator that has to come
# up quickly. Since it's not needed until after the first line has been
# entered, I'm throwing up a loader in a thread. Blame nickjohnson if it's bad
import threading
pint_load_event = threading.Event()
pint=None
UREG=None
def pintloader():
    global pint, _num_parser, UREG, _Q_
    try:
        import pint
        UREG = pint.UnitRegistry ()
        UREG.autoconvert_offset_to_baseunit = True
        def _num_parser(x):
            # Do not return int!
            ret = UREG.parse_expression (x)
            if isinstance (ret, int):
                return float (ret)
            else:
                return ret
        def _Q_(x):
            return UREG.parse_expression (x)
        pint_load_event.set ()
    except ImportError:
        pint = None
        _num_parser = float
        def _Q_(x):
            return float (x.partition(" ")[0])
        pint_load_event.set ()

pL = threading.Thread(target=pintloader)
pL.start()

def num_parser(x):
    pint_load_event.wait()
    if '"' in x:
        x, delim, tag = x.partition('"')
    else:
        tag = None
    parsed_num = _num_parser(x)
    if tag is None:
        return parsed_num
    else:
        return Tagged (parsed_num, tag.strip())

def Q_(*args, **kwargs):
    pint_load_event.wait()
    return _Q_(*args, **kwargs)

class UndoStack (list):
    """Stack supporting an 'undo' action.
    This is used as the main RPN stack. You can append() and pop() and [] just
    like with a normal list. You can also use undopush() to push a duplicate of
    the stack itself onto a "stack of stacks", and then undo() to restore that.
    """

    def __init__ (self, v=None):
        """Initialize an UndoStack from an optional source list.
        """
        if v is None:
            list.__init__(self)
            self.__sos = [[]]

        else:
            list.__init__(self, v)
            self.__sos = [[]]

    def undopush (self):
        """Save the current stack state to be restored later with undo()
        """
        self.__sos.append (self[:])

    def undo (self):
        """Restore the last saved undo state
        """
        if len (self.__sos) > 1:
            self[:] = self.__sos.pop ()
        else:
            self[:] = []

class Tagged (object):
    """Tagged number object.
    This behaves like a number, but also contains a string tag. The values
    are accessible at .num and .tag
    """
    def __init__ (self, num, tag):
        self._num = num
        self._tag = tag

    @property
    def num (self):
        return self._num

    @property
    def tag (self):
        return self._tag

# Add operations to Tagged
ops = [
        ("add", lambda x,y: x+y),
        ("sub", lambda x,y: x-y),
        ("mul", lambda x,y: x*y),
        ("truediv", lambda x,y: x/y),
        ("mod", lambda x,y: x%y),
        ("pow", lambda x,y: x**y),
        ]
for opname, opfunc in ops:
    # For the uninitiated, the default-argument parameters create a new
    # scope for the variable, allowing passing each loop iteration's value
    # to the closure instead of closing around the single final value.
    def method (self, other, opfunc=opfunc):
        if isinstance (other, Tagged):
            # If both are tagged, just remove the tag.
            return opfunc (self.num, other.num)
        if not isinstance (other, float): return NotImplemented
        return Tagged (opfunc (self.num, other), self.tag)
    def rmethod (self, other, opfunc=opfunc):
        if isinstance (other, Tagged):
            # If both are tagged, just remove the tag.
            return opfunc (other.num, self.num)
        if not isinstance (other, float): return NotImplemented
        return Tagged (opfunc (other, self.num), self.tag)
    setattr (Tagged, "__%s__" % opname, method)
    setattr (Tagged, "__r%s__" % opname, rmethod)

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
def eng(x, sigfigs=7):
    """Return x in engineering notation"""
    if x == 0.0:
        return "0"
    elif x < 0.0:
        return '-'+eng (-x, sigfigs)
    m = math.floor(math.log10(x)/3)*3
    coeff = "{0:.{1}g}".format (x * 10.0 ** (-m), sigfigs)
    lut = LUT.get (m, None)
    if lut is None:
        return coeff + "e" + str (m)
    if lut != '': lut = '_' + lut
    #if '.' in coeff and lut != '':
    #    return coeff.replace ('.', lut)
    #else:
    #    return coeff + lut
    return (coeff + lut)
