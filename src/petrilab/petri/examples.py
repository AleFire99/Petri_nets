"""Nets from the design docs (docs/petri/*.md)."""

from petrilab.petri.model import PTNet


def water() -> PTNet:
    n = PTNet("water")
    n.add_place("H2", 4)
    n.add_place("O2", 2)
    n.add_place("H2O")
    n.add_transition("react", {"H2": 2, "O2": 1}, {"H2O": 2})
    return n


def bounded_counter(*, inhibited: bool = True, limit: int = 2) -> PTNet:
    n = PTNet("bounded_counter")
    n.add_place("Buf")
    n.add_transition(
        "put", post={"Buf": 1}, inhibit={"Buf": limit} if inhibited else None
    )
    n.add_transition("get", pre={"Buf": 1})
    return n


def read_arc_net(*, key: bool = True) -> PTNet:
    n = PTNet("read_arc")
    n.add_place("Key", 1 if key else 0)
    n.add_place("Job", 2)
    n.add_place("Done")
    n.add_transition("use", {"Job": 1}, {"Done": 1}, read={"Key": 1})
    return n


def producer_consumer(capacity: int = 2) -> PTNet:
    n = PTNet(f"producer_consumer_{capacity}")
    n.add_place("ProdIdle", 1)
    n.add_place("Free", capacity)
    n.add_place("Buffer")
    n.add_place("ConsIdle", 1)
    n.add_transition(
        "produce", {"ProdIdle": 1, "Free": 1}, {"ProdIdle": 1, "Buffer": 1}
    )
    n.add_transition(
        "consume", {"Buffer": 1, "ConsIdle": 1}, {"Free": 1, "ConsIdle": 1}
    )
    return n


def dining_philosophers(n_phil: int = 2, *, atomic: bool = False) -> PTNet:
    """Philosopher i takes Fork_i (left) then Fork_{i+1} (right); ``atomic`` takes both at once."""
    if n_phil < 2:
        raise ValueError("need at least two philosophers")
    net = PTNet(f"philosophers_{n_phil}_{'atomic' if atomic else 'naive'}")
    for i in range(n_phil):
        net.add_place(f"Think{i}", 1)
        net.add_place(f"Fork{i}", 1)
        net.add_place(f"Eat{i}")
        if not atomic:
            net.add_place(f"HasLeft{i}")
    for i in range(n_phil):
        left, right = f"Fork{i}", f"Fork{(i + 1) % n_phil}"
        if atomic:
            net.add_transition(
                f"take{i}", {f"Think{i}": 1, left: 1, right: 1}, {f"Eat{i}": 1}
            )
        else:
            net.add_transition(
                f"takeLeft{i}", {f"Think{i}": 1, left: 1}, {f"HasLeft{i}": 1}
            )
            net.add_transition(
                f"takeRight{i}", {f"HasLeft{i}": 1, right: 1}, {f"Eat{i}": 1}
            )
        net.add_transition(
            f"done{i}", {f"Eat{i}": 1}, {f"Think{i}": 1, left: 1, right: 1}
        )
    return net


def mutex() -> PTNet:
    n = PTNet("mutex")
    n.add_place("Mutex", 1)
    for k in (1, 2):
        n.add_place(f"Idle{k}", 1)
        n.add_place(f"Wait{k}")
        n.add_place(f"Crit{k}")
        n.add_transition(f"request{k}", {f"Idle{k}": 1}, {f"Wait{k}": 1})
        n.add_transition(f"enter{k}", {f"Wait{k}": 1, "Mutex": 1}, {f"Crit{k}": 1})
        n.add_transition(f"leave{k}", {f"Crit{k}": 1}, {f"Idle{k}": 1, "Mutex": 1})
    return n


def traffic_crossing() -> PTNet:
    n = PTNet("traffic_crossing")
    n.add_place("Safe", 1)
    for road in ("NS", "EW"):
        n.add_place(f"{road}_Red", 1)
        n.add_place(f"{road}_Green")
        n.add_transition(
            f"{road.lower()}Go", {f"{road}_Red": 1, "Safe": 1}, {f"{road}_Green": 1}
        )
        n.add_transition(
            f"{road.lower()}Stop", {f"{road}_Green": 1}, {f"{road}_Red": 1, "Safe": 1}
        )
    return n
