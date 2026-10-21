"""Command line entry point.

    python -m factory_qc gdgddgf dddgkgf gdegf
"""

import sys

from .dfa import run
from .regex import matches


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 1
    for log in argv:
        result = run(log)
        print(f"\nInput: {log}")
        print(result.table())
        print(f"Regular expression agrees: {matches(log) == result.accepted}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
