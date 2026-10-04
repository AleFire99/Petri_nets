import itertools

from petrilab.fsm.parallel import TextStyle

REGIONS = ("bold", "italic", "underline")


def styles(sm: TextStyle) -> tuple[bool, ...]:
    active = {s.id for s in sm.configuration}
    return tuple(f"{r}_on" in active for r in REGIONS)


def test_initial_all_off() -> None:
    assert styles(TextStyle()) == (False, False, False)


def test_toggle_is_independent() -> None:
    sm = TextStyle()
    sm.send("toggle_bold")
    assert styles(sm) == (True, False, False)
    sm.send("toggle_underline")
    assert styles(sm) == (True, False, True)
    sm.send("toggle_bold")
    assert styles(sm) == (False, False, True)


def test_all_eight_combinations_reachable() -> None:
    seen = set()
    for mask in itertools.product([False, True], repeat=3):
        sm = TextStyle()
        for region, on in zip(REGIONS, mask, strict=True):
            if on:
                sm.send(f"toggle_{region}")
        seen.add(styles(sm))
    assert len(seen) == 8
