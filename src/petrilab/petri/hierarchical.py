"""Hierarchical nets by flattening substitution transitions (docs/petri/hierarchical.md)."""

from dataclasses import dataclass

from petrilab.petri.model import PTNet


@dataclass
class Subnet:
    """A subnet with an input port place and an output port place."""

    net: PTNet
    input_port: str
    output_port: str


def flatten(top: PTNet, subnets: dict[str, Subnet]) -> PTNet:
    """Replace each substitution transition by its subnet.

    The subnet's input port is fused with the (single) place feeding the substitution transition
    and its output port with the (single) place it feeds. Internal places/transitions are
    prefixed ``<substitution>.``.
    """
    flat = PTNet(f"{top.name}_flat")
    for p, tokens in top.places.items():
        flat.add_place(p, tokens)
    for t, spec in top.transitions.items():
        if t not in subnets:
            flat.add_transition(
                t, spec.pre, spec.post, inhibit=spec.inhibit, read=spec.read
            )
            continue
        sub = subnets[t]
        if len(spec.pre) != 1 or len(spec.post) != 1:
            raise ValueError(
                f"substitution {t!r} needs exactly one input and one output place"
            )
        (src,) = spec.pre
        (dst,) = spec.post
        rename = {sub.input_port: src, sub.output_port: dst}

        def local(
            p: str, prefix: str = f"{t}.", rename: dict[str, str] = rename
        ) -> str:
            return rename.get(p, prefix + p)

        for p, tokens in sub.net.places.items():
            if p not in rename:
                flat.add_place(local(p), tokens)
        for st, sspec in sub.net.transitions.items():
            flat.add_transition(
                f"{t}.{st}",
                {local(p): w for p, w in sspec.pre.items()},
                {local(p): w for p, w in sspec.post.items()},
            )
    return flat


def pay_subnet() -> Subnet:
    n = PTNet("pay")
    for p in ("in", "mid", "out"):
        n.add_place(p)
    n.add_transition("authorise", {"in": 1}, {"mid": 1})
    n.add_transition("capture", {"mid": 1}, {"out": 1})
    return Subnet(n, "in", "out")


def order_top() -> PTNet:
    n = PTNet("order")
    n.add_place("Ordered", 1)
    n.add_place("Paid")
    n.add_place("Shipped")
    n.add_transition("Pay", {"Ordered": 1}, {"Paid": 1})  # substitution transition
    n.add_transition("ship", {"Paid": 1}, {"Shipped": 1})
    return n
