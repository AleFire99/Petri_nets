# Agent rules for xstate/

The model is the source of truth. Python in `src/petrilab/fsm/` follows it and is proven by replaying `generated/*/vectors.json`.

## Machines (`src/machines/*.machine.ts`)
1. `setup({ types, guards, actions, delays }).createMachine({...})`.
2. Keep the config literal (no loops or helpers building states) so the VS Code visual editor can parse it. Exception: analysis-only factories such as `createPhilosophers`.
3. Guards, actions, delays: named and implemented in `setup`. Parameters via `params`.
4. Timers: named delays + `after`. Never `setTimeout`.
5. Outputs: UPPER_CASE state `tags`, one tag per physical output.
6. Keep context finite (bounded counters, no timestamps). Otherwise set `maxDepth` in the spec and say why.
7. When a machine mirrors a Python implementation, use the same state ids and context names.

## Specs (`src/specs/`)
- Every machine has a spec: `slug`, `events` (each payload variant), `marked`, `invariants`, `expect`.
- Register it in `src/specs/index.ts`.
- Never weaken an invariant or change `expect` to get green without saying so in the PR.

## Workflow
1. Edit machine and spec.
2. `npm run verify` until green. Read the counterexample traces.
3. Scenario tests with `SimulatedClock` in `test/`; test timer edges at `delay - 1` and `delay`.
4. Commit machine, spec, tests and `generated/` together.
5. From the repo root: `uv run pytest` (vector replay and Petri cross-checks).

## Never
- Edit `generated/` by hand.
- Use real time in tests.
