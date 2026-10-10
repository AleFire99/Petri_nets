# xstate/

Every FSM in the repo, as XState v5 machines: designed visually or as text, simulated, checked exhaustively. Background and results: [fsm/docs/xstate.md](../docs/xstate.md).

```bash
npm ci
npm run verify          # typecheck + export + analyze + vitest
npm run analyze         # exhaustive checks with counterexample traces
npm run export          # regenerate generated/ (commit it)
npm run sim -- washer   # interactive simulator; `--inspect` streams to Stately Inspector
```

| Path | Content |
|------|---------|
| `src/machines/` | One file per design. Open in VS Code, click **Open Visual Editor** above `createMachine`. |
| `src/specs/` | Events, home states, invariants, expected results per machine; `index.ts` registers them. |
| `src/analysis/explore.ts` | Exhaustive explorer: deadlock, blocking, invariants, reachability. |
| `src/codegen/` | Mermaid, test vectors, IEC 61131-3 Structured Text skeleton. |
| `test/` | vitest: scenarios per design, exhaustive analysis, vector replay on the live interpreter. |
| `generated/diagrams/` | Mermaid diagram per machine (PR review). |
| `generated/vectors/` | Test vectors for hand-written implementations (`tests/fsm/` replays them). |
| `generated/st/` | ST function-block skeletons. |
| `generated/reports/` | State-space counts read by the Petri cross-check (`tests/petri/test_xstate_crosscheck.py`). |

| Machine | Design |
|---------|--------|
| `trafficLight`, `turnstile` | [regular](../docs/regular.md) |
| `mediaPlayer` | [hierarchical](../docs/hierarchical.md) |
| `vendingMachine` | [extended](../docs/extended.md) |
| `doorAlarm` | [timed](../docs/timed.md) |
| `washer` | [history](../docs/history.md) |
| `textStyle` | [parallel](../docs/parallel.md) |
| `elevenDetector` | [Moore vs Mealy](../docs/moore-mealy.md) |
| `fillStation` | [fill station](../docs/fill-station.md), Python in `src/petrilab/fsm/fill_station.py` |
| `philosophers{n}{Naive,Atomic}` | `dining_philosophers()` in `src/petrilab/petri/examples.py` |
