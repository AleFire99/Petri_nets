import random

from petrilab.fsm.moore_mealy import MealyDetector, MooreDetector

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
