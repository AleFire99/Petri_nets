# FSM with history

A pseudo-state that remembers the last active child of a composite state. **Shallow** history restores only the direct child (entering it at its default sub-state); **deep** history restores the full nested configuration.

## Use case
Washing machine: `pause` interrupts a cycle, `resume` returns to where it was.

```mermaid
stateDiagram-v2
    [*] --> Off
    Off --> Running: start
    state Running {
        [*] --> Fill
        Fill --> Wash: filled
        state Wash {
            [*] --> Soak
            Soak --> Agitate: soaked
        }
        Wash --> Spin: washed
    }
    Running --> Paused: pause
    Paused --> Running: resume (history)
    Running --> Off: stop
    Paused --> Off: stop
```

Variants of `resume`:

| Kind | Pause during `Wash.Agitate` then resume enters |
|------|------------------------------------------------|
| Shallow | `Wash.Soak` (Wash restored, its default child) |
| Deep | `Wash.Agitate` (exact configuration) |
| None | `Fill` (initial) |

| From | Event | To |
|------|-------|----|
| Off | start | Running.Fill |
| Fill | filled | Wash.Soak |
| Soak | soaked | Wash.Agitate |
| Wash | washed | Spin |
| Running | pause | Paused |
| Paused | resume | Running (history) |
| Running, Paused | stop | Off |

## In XState
Machine: [`washer.machine.ts`](../../xstate/src/machines/washer.machine.ts) (washer (input `history`: deep / shallow / none)). Scenario tests: [`designs.unit.test.ts`](../../xstate/test/designs.unit.test.ts). Resume after `agitate` gives `agitate` (deep), `soak` (shallow), `fill` (none). Checked for each kind: drum and valve never on together, `off` always reachable. Remembered history is part of state identity in the explorer (29 states, not 6).
