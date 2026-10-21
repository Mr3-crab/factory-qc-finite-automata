import itertools

import pytest

from factory_qc import ALPHABET, TRANSITIONS, accepts, matches, run


# --- the three traces from the report -------------------------------------

def test_trace_1_isolated_defect_then_warning_is_accepted():
    result = run("gdgddgf")
    assert [s.next for s in result.steps] == ["q0", "q1", "q0", "q1", "q2", "q0", "q5"]
    assert result.accepted


def test_trace_2_halt_then_supervisor_reset_is_accepted():
    result = run("dddgkgf")
    assert [s.next for s in result.steps] == ["q1", "q2", "q3", "q3", "q0", "q0", "q5"]
    assert result.accepted


def test_trace_3_uncleared_emergency_stop_is_rejected():
    result = run("gdegf")
    assert result.final_state == "q4"
    assert not result.accepted


# --- business requirements --------------------------------------------------

def test_good_bag_resets_the_count():
    assert run("dg").final_state == "q0"
    assert run("ddg").final_state == "q0"


def test_warning_at_two_and_halt_at_three():
    assert run("dd").final_state == "q2"
    assert run("ddd").final_state == "q3"


def test_halted_line_cannot_restart_on_its_own():
    for noise in ("g", "d", "f", "gggg"):
        assert run("ddd" + noise).final_state == "q3"


def test_key_switch_has_no_effect_while_running():
    for prefix in ("", "d", "dd"):
        before = run(prefix).final_state
        assert run(prefix + "k").final_state == before


@pytest.mark.parametrize("prefix", ["", "d", "dd", "ddd", "e"])
def test_emergency_stop_from_any_operating_state(prefix):
    assert run(prefix + "e").final_state == "q4"
    assert run(prefix + "ek").final_state == "q0"


def test_events_after_shift_end_are_rejected_early():
    result = run("fgdddd")
    assert result.stopped_early and len(result.steps) == 2
    assert not result.accepted


def test_empty_log_is_rejected():
    assert not accepts("")


def test_unknown_symbol_raises():
    with pytest.raises(ValueError):
        run("gx")


# --- formal properties -----------------------------------------------------

def test_transition_function_is_total_and_deterministic():
    assert len(TRANSITIONS) == 7
    for state, row in TRANSITIONS.items():
        assert set(row) == set(ALPHABET)          # complete: 7 x 5 = 35 entries
        assert all(isinstance(t, str) for t in row.values())


def test_regular_expression_matches_dfa_on_every_short_string():
    # The report checks lengths 0-8 (488,281 strings); 0-6 keeps CI fast.
    for n in range(7):
        for t in itertools.product(ALPHABET, repeat=n):
            s = "".join(t)
            assert matches(s) == accepts(s), s
