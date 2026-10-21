"""Deterministic finite automaton for the packaging-line quality controller.

Each symbol is one event recorded during a production shift:

    g  good bag passes the optical sensor
    d  defective bag (torn packaging or underweight)
    e  emergency-stop button pressed
    k  supervisor key-switch reset
    f  end of shift

A shift log is accepted when the shift closes while the line is running,
i.e. every halt or emergency stop raised during the shift was cleared.
"""

from dataclasses import dataclass, field

ALPHABET = ("g", "d", "e", "k", "f")

STATE_NAMES = {
    "q0": "Normal",
    "q1": "Defect1",
    "q2": "Warning",
    "q3": "Halted",
    "q4": "E-Stop",
    "q5": "Shift Complete",
    "q6": "Trap",
}

START = "q0"
ACCEPTING = frozenset({"q5"})

# delta : Q x Sigma -> Q  (Table 9 in the report)
TRANSITIONS = {
    "q0": {"g": "q0", "d": "q1", "e": "q4", "k": "q0", "f": "q5"},
    "q1": {"g": "q0", "d": "q2", "e": "q4", "k": "q1", "f": "q5"},
    "q2": {"g": "q0", "d": "q3", "e": "q4", "k": "q2", "f": "q5"},
    "q3": {"g": "q3", "d": "q3", "e": "q4", "k": "q0", "f": "q3"},
    "q4": {"g": "q4", "d": "q4", "e": "q4", "k": "q0", "f": "q4"},
    "q5": {"g": "q6", "d": "q6", "e": "q6", "k": "q6", "f": "q6"},
    "q6": {"g": "q6", "d": "q6", "e": "q6", "k": "q6", "f": "q6"},
}

TRAP = "q6"


@dataclass
class Step:
    index: int
    current: str
    symbol: str
    next: str


@dataclass
class RunResult:
    accepted: bool
    final_state: str
    steps: list = field(default_factory=list)
    stopped_early: bool = False

    def table(self):
        rows = ["Step | Current | Input | Next", "-----|---------|-------|-----"]
        for s in self.steps:
            rows.append(f"{s.index:>4} | {s.current:<7} | {s.symbol:^5} | {s.next}")
        verdict = "ACCEPT" if self.accepted else "REJECT"
        rows.append(f"Result: {verdict} (final state {self.final_state})")
        return "\n".join(rows)


def run(events, early_exit=True):
    """Feed a sequence of events through the DFA.

    `events` can be a string such as "gdgddgf" or any iterable of symbols.
    With early_exit=True the run stops as soon as the trap state is reached,
    which is the O(1) best case discussed in Part B of the report.
    """
    state = START
    steps = []
    for i, symbol in enumerate(events, start=1):
        if symbol not in ALPHABET:
            raise ValueError(f"unknown event {symbol!r} at position {i}")
        nxt = TRANSITIONS[state][symbol]
        steps.append(Step(i, state, symbol, nxt))
        state = nxt
        if early_exit and state == TRAP:
            return RunResult(False, state, steps, stopped_early=True)
    return RunResult(state in ACCEPTING, state, steps)


def accepts(events):
    return run(events).accepted
