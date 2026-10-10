# FSM designs

FSMs are designed, simulated and verified in XState v5, in the subproject [`fsm/xstate/`](../xstate/README.md). Start with the [workflow](xstate.md). Each design below is a Markdown page (description, use case, Mermaid diagram, transition table) plus one XState machine that is checked exhaustively in CI.

| # | Design | Variant | Example | Machine |
|---|--------|---------|---------|---------|
| 1 | [Regular](regular.md) | flat, deterministic | traffic light, turnstile | `regular.machine.ts` |
| 2 | [Hierarchical](hierarchical.md) | nested states | media player | `mediaPlayer.machine.ts` |
| 3 | [Extended](extended.md) | guards + context variables | vending machine | `vendingMachine.machine.ts` |
| 4 | [Timed](timed.md) | timeouts | door alarm | `doorAlarm.machine.ts` |
| 5 | [History](history.md) | shallow / deep history | washing machine | `washer.machine.ts` |
| 6 | [Parallel](parallel.md) | orthogonal regions | text styling | `textStyle.machine.ts` |
| 7 | [Moore vs Mealy](moore-mealy.md) | output models | "11" detector | `elevenDetector.machine.ts` |
| 8 | [Fill station](fill-station.md) | all of the above in one control EFSM | tank fill / heat / drain | `fillStation.machine.ts` + Python implementation |

Why XState and not a Python statechart library: [library evaluation](library-evaluation.md).
