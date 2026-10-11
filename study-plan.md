# Study plan: Petri nets, coloured Petri nets, EFSMs

Ten modules, about one week each at 4–6 hours a week. Every module has the same shape: **read** (theory in `docs/`), **run** (examples and notebooks), **code** (the implementation in `src/petrilab/`), **test** (its pytest file), **practise** (exercises), and a **checkpoint** you should be able to answer without notes.

Setup is in the [README](README.md#quick-start). Bibliography: [docs/references.md](docs/references.md).

```text
Part I   P/T nets      M1 basics → M2 behaviour → M3 linear algebra → M4 unbounded nets
Part II  CPNs          M5 colours and bindings → M6 folding, unfolding, verification
Part III EFSMs         M7 FSM → EFSM → M8 verification and model-based testing
Part IV  Extensions    M9 time, probability, hierarchy, workflows
Capstone               M10 one system in three formalisms
```

## Learning objectives

By the end you can:
1. State the formal definitions of P/T nets, CPNs and EFSMs and execute each by hand.
2. Decide boundedness, safeness, deadlock freedom, liveness and reversibility of small nets, and say which analysis technique applies (reachability graph, coverability graph, invariants, state equation).
3. Fold a P/T net into a CPN, unfold a CPN into a P/T net, and move results between them.
4. Design EFSMs with deterministic guards, verify invariants by bounded exploration, and read counterexample traces.
5. Generate transition-coverage tests from a model and use them to prove a hand-written implementation (and to kill mutants).
6. Implement and test all of the above in typed Python with pytest.

---

## Part I: place/transition nets

### M1 · Nets, markings, firing
- **Read:** [foundations](docs/petri/foundations.md) §1–2, [place/transition net](docs/petri/place-transition.md); Murata (1989) §I–III.
- **Run:** `uv run python examples/pt_firing_and_invariants.py` (first half); notebook `notebooks/petri/place_transition.ipynb`.
- **Code:** [`model.py`](src/petrilab/petri/model.py): `PTNet.enabled`, `fire`, `marking`.
- **Test:** [`test_model.py`](tests/petri/test_model.py), [`test_place_transition.py`](tests/petri/test_place_transition.py).
- **Practise:** [P1](exercises/petri/p1-parking-lot.md), [P2](exercises/petri/p2-traffic-light.md).
- **Checkpoint:** fire the producer/consumer net by hand from `M0` to `(1, 0, 2, 1)`; explain why `consume` is not enabled in `M0`; say what a self-loop does to `C`.

### M2 · Behavioural properties and the reachability graph
- **Read:** [foundations](docs/petri/foundations.md) §3–4, [inhibitor and read arcs](docs/petri/inhibitor-read.md), [classic examples](docs/petri/examples.md).
- **Run:** `uv run python examples/reachability_deadlock.py`; notebooks `examples.ipynb`, `extended_arcs.ipynb`.
- **Code:** `PTNet.reachable`, `PTNet.trace_to`; [`analysis.py`](src/petrilab/petri/analysis.py) (dead markings, liveness by terminal SCCs); [`snakes_bridge.py`](src/petrilab/petri/snakes_bridge.py).
- **Test:** [`test_examples.py`](tests/petri/test_examples.py), [`test_trace_to.py`](tests/petri/test_trace_to.py), [`test_extended_arcs.py`](tests/petri/test_extended_arcs.py).
- **Practise:** [P3](exercises/petri/p3-lock-ordering.md).
- **Checkpoint:** define L0–L4 liveness; give a deadlock-free net that is not live; explain why liveness on a finite graph reduces to terminal SCCs.

### M3 · Linear algebra: incidence matrix, state equation, invariants
- **Read:** [foundations](docs/petri/foundations.md) §5–7; Murata (1989) §VI–VII.
- **Run:** second half of `examples/pt_firing_and_invariants.py`.
- **Code:** [`invariants.py`](src/petrilab/petri/invariants.py) (integer nullspace with sympy).
- **Test:** invariant tests in [`test_examples.py`](tests/petri/test_examples.py) and [`test_place_transition.py`](tests/petri/test_place_transition.py).
- **Practise:** [P4](exercises/petri/p4-mutex-invariants.md), [P6](exercises/petri/p6-state-equation.md).
- **Checkpoint:** prove mutual exclusion of `examples.mutex()` from one P-invariant; give a marking that solves the state equation but is unreachable.

### M4 · Unbounded nets: coverability
- **Read:** [coverability](docs/petri/coverability.md); Karp and Miller (1969) or Peterson (1981) ch. 4; [foundations](docs/petri/foundations.md) §8 (decidability).
- **Run:** `uv run python examples/coverability_unbounded.py`.
- **Code:** [`coverability.py`](src/petrilab/petri/coverability.py).
- **Test:** [`test_coverability.py`](tests/petri/test_coverability.py) (bounded nets give the reachability graph; ω; inhibitor arcs rejected).
- **Practise:** [P5](exercises/petri/p5-coverability.md).
- **Checkpoint:** run Karp-Miller by hand on a 2-place net; list two questions the coverability graph cannot answer and why.

## Part II: coloured Petri nets

### M5 · Colour sets, multisets, bindings
- **Read:** [CPN formal](docs/petri/cpn-formal.md) §1–4, [coloured net](docs/petri/colored.md); Jensen and Kristensen (2009) ch. 2–4.
- **Run:** `uv run python examples/cpn_bindings_and_unfolding.py` (jobs part); notebook `colored.ipynb`.
- **Code:** [`cpn.py`](src/petrilab/petri/cpn.py): `enabled_bindings`, `fire`, `reachable`; [`cpn_examples.py`](src/petrilab/petri/cpn_examples.py).
- **Test:** [`test_cpn.py`](tests/petri/test_cpn.py) (firing rule, guards, colour errors), [`test_colored.py`](tests/petri/test_colored.py) (SNAKES).
- **Practise:** [C1](exercises/cpn/c1-odd-jobs.md).
- **Checkpoint:** write the enabling condition with multisets; compute the enabled bindings of `takeRight` after `takeLeft<p=1>` in the 3-philosopher CPN.

### M6 · Folding, unfolding, verification of CPNs
- **Read:** [CPN formal](docs/petri/cpn-formal.md) §5–7; Jensen and Kristensen (2009) ch. 7–9 (state spaces).
- **Run:** philosophers and unfolding part of `examples/cpn_bindings_and_unfolding.py`.
- **Code:** `unfold`, `to_pt_marking`, `CPN.trace_to`.
- **Test:** isomorphism and invariant tests in [`test_cpn.py`](tests/petri/test_cpn.py).
- **Practise:** [C2](exercises/cpn/c2-folded-crossing.md), [C3](exercises/cpn/c3-unfolding-invariants.md), [C4](exercises/cpn/c4-resource-ordering.md).
- **Checkpoint:** how many places and transitions does the unfolding of a CPN have; state the fork invariant of the philosophers; explain why resource ordering removes the deadlock.

## Part III: extended finite state machines

### M7 · From FSMs to EFSMs
- **Read:** [regular](docs/fsm/regular.md), [Moore vs Mealy](docs/fsm/moore-mealy.md), [extended](docs/fsm/extended.md), [EFSM formal](docs/fsm/efsm-formal.md) §1–3; Cheng and Krishnakumar (1993); Harel (1987) for statecharts.
- **Run:** first part of `uv run python examples/efsm_vending.py`; in `xstate/`: `npm run sim` (see [XState workflow](docs/fsm/xstate.md)).
- **Code:** [`efsm.py`](src/petrilab/fsm/efsm.py) (`EFSM`, `Machine`, `Transition`), [`vending_machine.py`](src/petrilab/fsm/vending_machine.py); compare with [`vendingMachine.machine.ts`](xstate/src/machines/vendingMachine.machine.ts).
- **Test:** [`test_efsm.py`](tests/fsm/test_efsm.py) (priority, ignored and invalid events, invalid definitions).
- **Practise:** [E1](exercises/efsm/e1-turnstile.md), [E2](exercises/efsm/e2-pin-lock.md).
- **Checkpoint:** define configuration, determinism and completeness; explain the three ways an event can fail to fire (unknown, ignored, strict error) and when each is right.

### M8 · Verification and model-based testing
- **Read:** [EFSM formal](docs/fsm/efsm-formal.md) §4–6, [XState workflow](docs/fsm/xstate.md), [fill station](docs/fsm/fill-station.md); Lee and Yannakakis (1996) §1–4.
- **Run:** rest of `examples/efsm_vending.py`; `examples/fill_station_behaviour.py`; in `xstate/`: `npm run verify`.
- **Code:** `explore`, `Exploration.violations`, `nondeterministic_choices`; [`fill_station.py`](src/petrilab/fsm/fill_station.py).
- **Test:** [`test_vending_machine.py`](tests/fsm/test_vending_machine.py) and [`test_fill_station.py`](tests/fsm/test_fill_station.py) (XState vectors and report), [`test_xstate_crosscheck.py`](tests/petri/test_xstate_crosscheck.py) (EFSM vs Petri net).
- **Practise:** [E3](exercises/efsm/e3-find-the-bug.md), [E4](exercises/efsm/e4-test-generation.md).
- **Checkpoint:** why is a BFS counterexample the shortest; what does "no violation at depth k" prove; why are paths of the configuration graph always feasible while control-graph paths may not be.

## Part IV: extensions

### M9 · Time, probability, hierarchy, workflows
Pick at least two.
- **Timed nets:** [timed](docs/petri/timed.md), [`timed.py`](src/petrilab/petri/timed.py), [`test_timed.py`](tests/petri/test_timed.py). Timed FSMs: [timed FSM](docs/fsm/timed.md).
- **Stochastic nets:** [stochastic](docs/petri/stochastic.md), [`stochastic.py`](src/petrilab/petri/stochastic.py) (CTMC steady state vs M/M/1/K).
- **Hierarchy:** [hierarchical net](docs/petri/hierarchical.md), [hierarchical FSM](docs/fsm/hierarchical.md), [history](docs/fsm/history.md), [parallel](docs/fsm/parallel.md).
- **Workflow nets:** [workflow](docs/petri/workflow.md), [`workflow.py`](src/petrilab/petri/workflow.py) (soundness, PM4Py cross-check); van der Aalst (1998).
- **Checkpoint:** for each chosen topic, one property the untimed/flat/P/T analysis gets wrong.

## Capstone

### M10 · One system, three formalisms
Model a small controller of your choice (a two-lift elevator, a single-lane bridge, a bounded retransmission protocol) three ways and make them agree:
1. **EFSM in XState** with a spec in `xstate/src/specs/` (invariants, `expect`), exported vectors and report.
2. **CPN** with `cpn.py` (one colour set per kind of entity).
3. **P/T net** from `unfold`, with P-invariants for the safety properties.
4. **Python implementation** (plain code) proven against the vectors, plus at least two mutants killed.
5. **Cross-check test**: same number of states, edges and dead states in all three, as in [`test_xstate_crosscheck.py`](tests/petri/test_xstate_crosscheck.py).
6. A design page in `docs/` (Mermaid diagram, transition table, verified properties) linked from its index.

Done when `uv run pytest`, `uv run ruff check`, `uv run mypy src examples exercises/solutions`, `uv run python scripts/check_docs.py` and `npm run verify` are green.

## Going further
- Siphons and traps (Desel and Esparza 1995) for deadlock analysis without state spaces.
- Partial-order reduction and symbolic state spaces (Baier and Katoen 2008); LoLA and TINA for large nets.
- CPN Tools for timed and hierarchical CPNs (Kristensen, Christensen and Jensen 1998).
- SMT-based bounded model checking of EFSMs (`z3`), noted as a next step in the [library evaluation](docs/petri/library-evaluation.md).
