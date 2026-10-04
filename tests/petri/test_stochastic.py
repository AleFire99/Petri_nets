import pytest

from petrilab.petri.stochastic import expected_tokens, mm1k, steady_state, throughput


def test_mm1k_matches_analytic_distribution() -> None:
    n = mm1k(1.0, 2.0, 3)
    pi = steady_state(n)
    for k, expected in enumerate([8 / 15, 4 / 15, 2 / 15, 1 / 15]):
        assert pi[n.marking(Free=3 - k, Queue=k)] == pytest.approx(expected)
    assert sum(pi.values()) == pytest.approx(1.0)


def test_mm1k_metrics() -> None:
    n = mm1k(1.0, 2.0, 3)
    pi = steady_state(n)
    assert expected_tokens(n, pi, "Queue") == pytest.approx(
        (0 * 8 + 4 + 2 * 2 + 3) / 15
    )
    # accepted arrivals = completed services in steady state
    assert throughput(n, pi, "arrive") == pytest.approx(throughput(n, pi, "serve"))
