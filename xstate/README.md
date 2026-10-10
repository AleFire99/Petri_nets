# xstate/

XState v5 models of the petrilab designs, used as design and verification layer. Background and results: [docs/fsm/xstate.md](../docs/fsm/xstate.md).

```bash
npm ci
npm run verify          # typecheck + export + analyze + vitest
npm run analyze         # exhaustive checks with counterexample traces
npm run export          # regenerate generated/ (commit it)
npm run sim -- door     # interactive simulator; `--inspect` streams to Stately Inspector
```

| Path | Content |
|------|---------|
| `src/machines/` | Machines. Open in VS Code, click **Open Visual Editor** above `createMachine`. |
| `src/specs/` | Per machine: events, home states, invariants, expected results. `index.ts` registers them. |
| `src/analysis/explore.ts` | Exhaustive explorer: deadlock, blocking, invariants, reachability. |
| `src/codegen/` | Mermaid, test vectors, IEC 61131-3 Structured Text skeleton. |
| `generated/<slug>/` | Export output, read by the Python tests. Never edit by hand. |
| `test/` | vitest: scenarios, analysis, vectors on the live interpreter. |

| Machine | Mirrors |
|---------|---------|
| `fillStation` | [docs/fsm/fill-station.md](../docs/fsm/fill-station.md) → `src/petrilab/fsm/fill_station.py` |
| `doorAlarm` | [docs/fsm/timed.md](../docs/fsm/timed.md) → `src/petrilab/fsm/timed.py` |
| `vendingMachine` | [docs/fsm/extended.md](../docs/fsm/extended.md) → `src/petrilab/fsm/extended.py` |
| `philosophers{n}{Naive,Atomic}` | `dining_philosophers()` in `src/petrilab/petri/examples.py` |
