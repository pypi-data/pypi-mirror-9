"""Global environment

These variables are accessible to the entire lerpn instance.
"""

from . import nums

# Display format.
# One of the subclasses of DisplayMode from nums
FORMAT = nums.EngMode

# sys.exc_info() from the last exception caught
# This is used by the 'exc command to display the backtrace
ERROR = None

# The current stack object.
# Note that due to nested stack support, this can change from cycle to cycle.
STACK = None
