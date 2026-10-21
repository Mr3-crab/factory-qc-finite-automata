"""Regular expression obtained from the DFA by state elimination.

The textbook notation uses '+' for union. Python's `re` uses '|', so the
expression is translated before compiling.
"""

import re

E = "e(g+d+e+f)*k"            # emergency stop, ignored events, supervisor reset
H = f"d(g+d+f)*(k+{E})"       # third consecutive defect -> halt -> recovery

LOOP = f"g+k+{E}+dk*(g+{E}+dk*(g+{E}+{H}))"
CLOSE = "f+dk*(f+dk*f)"

REGEX = f"({LOOP})*({CLOSE})"

_compiled = re.compile(REGEX.replace("+", "|"))


def matches(events):
    return _compiled.fullmatch(events) is not None
