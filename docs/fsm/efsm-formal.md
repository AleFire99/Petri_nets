# Extended finite state machines (formal)

An EFSM is an FSM plus variables: transitions read and write a context, and fire only when a guard on the context and the event payload holds. The control graph stays small while behaviour depends on data. Informal design page: [extended.md](extended.md). This page gives the definitions, a hand-worked run, and the Python engine that is proven against the XState model.

## 1. From FSM to EFSM

A **Mealy machine** is `M = (S, s0, I, O, δ, λ)`: states, initial state, input and output alphabets, transition function `δ : S × I → S` and output function `λ : S × I → O`. Moore machines put the output on states (`λ : S → O`); see [moore-mealy.md](moore-mealy.md).

An **EFSM** (Cheng and Krishnakumar 1993) is a tuple `E = (S, s0, V, c0, I, O, T)`:

| Symbol | Meaning |
|--------|---------|
| `S`, `s0 ∈ S` | finite set of control states, initial state |
| `V` | context variables; a **valuation** `c : V → D` gives each a value |
| `c0` | initial valuation |
| `I` | events; an event `e` has a type and a payload (`insert(amount=25)`) |
| `O` | outputs (here: state tags or context changes) |
| `T` | transitions `t = (s, e, g, a, s')` |

For a transition `t = (s, e, g, a, s')`:
- `g(c, e) ∈ {true, false}` is the **guard** (predicate on context and event payload);
- `a(c, e)` is the **action** (update function), giving the new valuation `c'`;
- `s, s'` are source and target control states.

A **configuration** is `(s, c) ∈ S × D^V`: the real state of the machine. If every variable has a finite domain, the EFSM is a (much larger) FSM over configurations: an EFSM is a compressed FSM, just as a CPN is a compressed P/T net.

## 2. Semantics

- `t` is **enabled** in `(s, c)` for event `e` iff `t` starts in `s`, is labelled `e`, and `g(c, e)` holds.
- Firing gives `(s', a(c, e))`. A run is a sequence `(s0, c0) --e1--> (s1, c1) --e2--> ...`.
- **Deterministic**: in every configuration, at most one transition is enabled per event (guards on the same `(s, e)` are mutually exclusive).
- **Completely specified**: at least one is enabled for every event. Incompletely specified machines need a convention for the missing case.

| Choice | Textbook EFSM | XState v5 and [`efsm.py`](../../src/petrilab/fsm/efsm.py) |
|--------|---------------|-----------------------------------------------------------|
| Several guards true | forbidden (non-deterministic) | first in declaration order wins (priority) |
| No guard true | undefined or error | event ignored; `Machine(..., strict=True)` raises `InvalidTransitionError` |
| Event not in alphabet | undefined | `UnknownEventError` (always: it is a caller bug) |
| Actions | update function | pure function returning the changed variables (like `assign`) |

`nondeterministic_choices(...)` lists every configuration where priority decided, so you can check each overlap is intended (in the vending machine, `credit == price` also satisfies `credit >= price`; the `exact` branch is listed first on purpose).

## 3. Worked example: vending machine

`S = {idle, has_credit}`, `V = {credit, dispensed, rejected}`, `c0 = (0, 0, 0)`, `price = 75`. Transitions in priority order:

| # | From | Event | Guard | Action | To |
|---|------|-------|-------|--------|----|
| 1 | idle | insert(amount) | amount > 0 | credit += amount | has_credit |
| 2 | has_credit | insert(amount) | amount > 0 | credit += amount | has_credit |
| 3 | has_credit | select | credit == price | credit −= price; dispensed += 1 | idle |
| 4 | has_credit | select | credit ≥ price | credit −= price; dispensed += 1 | has_credit |
| 5 | has_credit | select | (else) | rejected += 1 | has_credit |
| 6 | has_credit | refund | | credit = 0 | idle |

Run, step by step (configuration written `state {credit, dispensed, rejected}`):

| Step | Event | Enabled | Fires | Configuration after |
|------|-------|---------|-------|---------------------|
| 0 | | | | `idle {0, 0, 0}` |
| 1 | insert(50) | 1 | 1 | `has_credit {50, 0, 0}` |
| 2 | select | 5 (50 < 75) | 5 | `has_credit {50, 0, 1}` |
| 3 | insert(50) | 2 | 2 | `has_credit {100, 0, 1}` |
| 4 | select | 4, 5 (100 ≥ 75) | 4 | `has_credit {25, 1, 1}` |
| 5 | refund | 6 | 6 | `idle {0, 1, 1}` |
| 6 | select | none | ignored | `idle {0, 1, 1}` |

```python
from petrilab.fsm.efsm import Machine
from petrilab.fsm.vending_machine import vending_machine

m = Machine(vending_machine())
for ev in ["insert", "select", "insert", "select", "refund", "select"]:
    m.send(ev, amount=50) if ev == "insert" else m.send(ev)
m.config  # Configuration(state='idle', context=(('credit', 0), ('dispensed', 1), ('rejected', 1)))
```

## 4. Verification by exploration

The configuration space is infinite here (`credit`, `dispensed`, `rejected` are unbounded), so exploration needs two finite abstractions:

1. **Finite environment**: a fixed set of event instances, e.g. coins `{0, 25, 50, 100}`, `select`, `refund`.
2. **Depth bound**: explore configurations at most `k` events from the start. Configurations at depth `k` form the **frontier**; they are not reported as deadlocks, and results hold only for the explored part (a *bounded* proof).

`explore(efsm, events, max_depth=4)` does a breadth-first search over configurations with the same counting rules as the XState explorer (an event that leaves the configuration unchanged is not an edge). For the vending machine at depth 4 both give **53 configurations and 129 edges**; [`test_vending_machine.py`](../../tests/fsm/test_vending_machine.py) asserts it against `xstate/generated/reports/vending-machine.json`.

On top of the exploration:

| Check | Function |
|-------|----------|
| Deadlock: fully expanded configuration with no outgoing edge | `Exploration.deadlocks()` |
| Safety invariant, with the shortest counterexample trace | `Exploration.violations({name: predicate})` |
| Unreachable control states | `set(efsm.states) - Exploration.visited_states()` |
| Overlapping guards | `nondeterministic_choices(efsm, exploration, events)` |

When context is genuinely unbounded, a bounded search can miss bugs deeper than `k`. Remedies: abstract the context (keep `credit mod price` and a flag instead of counters), prove the invariant inductively (show each transition preserves it), or use a symbolic tool (SMT).

## 5. Testing EFSMs

A model gives you the expected output of every test for free. Common coverage criteria, weakest first:

| Criterion | Test set |
|-----------|----------|
| State coverage | every control state visited |
| Transition coverage | every transition (of the explored configuration graph) taken at least once |
| Transition-pair / path coverage | consecutive pairs, or all paths up to length k |
| Checking sequences (W-method, Chow 1978) | for FSMs: distinguishes the implementation from every faulty machine with at most m states |

EFSM-specific difficulty: a path in the control graph may be **infeasible** because its guards cannot all hold (for example `select` taking transition 3 right after `insert(25)` from idle). Generating tests from the *configuration* graph avoids that: every path there is feasible by construction.

This repo uses transition coverage on the configuration graph: `npm run export` in [`xstate/`](../../xstate/README.md) writes one vector per explored edge (shortest path to the source, then the edge). Each step holds the expected state, outputs and context. The vending machine has 129 vectors and the Python engine replays all of them; exercise [E4](../../exercises/efsm/e4-test-generation.md) builds the same generator in Python.

## 6. EFSMs and Petri nets

| EFSM | CPN equivalent |
|------|----------------|
| configuration `(s, c)` | a single token `(s, c)` in one place `Ctrl` |
| transition `(s, e, g, a, s')` | CPN transition with input arc `(s, c)`, guard `g`, output arc `(s', a(c, e))` (one per event instance) |
| parallel regions (XState `type: 'parallel'`) | one token per region, or one place per region |
| context variable shared between regions | a separate place holding the variable's value |

So an EFSM is a CPN with exactly one token, and its reachability graph is the CPN's reachability graph. Going the other way, every bounded P/T net is an FSM over its reachable markings (its reachability graph). The cross-check [`test_xstate_crosscheck.py`](../../tests/petri/test_xstate_crosscheck.py) uses this: the dining philosophers as a parallel XState machine (forks in context) and as a P/T net have identical state, edge and deadlock counts for n = 2, 3, 4.

References: [references.md](../references.md).
