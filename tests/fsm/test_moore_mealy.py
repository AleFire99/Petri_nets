import random

from automata.fa.dfa import DFA

from petrilab.fsm.moore_mealy import MEALY, MealyDetector, MooreDetector

BITS = [0, 1, 1, 0, 1, 1, 1]


def test_mealy_known_stream() -> None:
    assert MealyDetector().run(BITS) == [0, 0, 1, 0, 0, 1, 1]


def test_moore_known_stream() -> None:
    assert MooreDetector().run(BITS) == [0, 0, 1, 0, 0, 1, 1]


def test_equivalent_on_random_streams() -> None:
    rng = random.Random(0)
    for _ in range(200):
        bits = [rng.randint(0, 1) for _ in range(rng.randint(0, 30))]
        assert MealyDetector().run(bits) == MooreDetector().run(bits)


def _mealy_dfa() -> DFA:
    """Accepts the input words whose last Mealy output is 1 (states: (state, last output))."""
    transitions: dict[str, dict[str, str]] = {}
    for state, last in [("S0", 0), ("S1", 0), ("S1", 1), ("S0", 1)]:
        transitions[f"{state}/{last}"] = {
            str(bit): "{}/{}".format(*MEALY[(state, bit)]) for bit in (0, 1)
        }
    return DFA(
        states=set(transitions),
        input_symbols={"0", "1"},
        transitions=transitions,
        initial_state="S0/0",
        final_states={q for q in transitions if q.endswith("/1")},
    )


def _moore_dfa() -> DFA:
    """Accepts the input words that end in a state whose output is 1."""
    transitions: dict[str, dict[str, str]] = {s.id: {} for s in MooreDetector.states}
    for state in MooreDetector.states:
        for tr in state.transitions:
            bit = "1" if next(iter(tr.events)).id == "one" else "0"
            transitions[state.id][bit] = next(iter(tr.targets)).id
    return DFA(
        states=set(transitions),
        input_symbols={"0", "1"},
        transitions=transitions,
        initial_state="a",
        final_states={q for q, out in MooreDetector.OUTPUT.items() if out == 1},
    )


def test_equivalent_by_dfa_equivalence() -> None:
    """Exact proof: equal languages means equal last output after every prefix."""
    assert _mealy_dfa() == _moore_dfa()
    broken = DFA(
        states={"a", "b", "c"},
        input_symbols={"0", "1"},
        transitions={
            "a": {"0": "a", "1": "b"},
            "b": {"0": "a", "1": "c"},
            "c": {"0": "a", "1": "c"},
        },
        initial_state="a",
        final_states={"b"},
    )
    assert _mealy_dfa() != broken
