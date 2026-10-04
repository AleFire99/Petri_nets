# Moore vs Mealy

- **Moore**: output depends on the current state only.
- **Mealy**: output depends on the current state and the input (emitted on transitions).

## Use case
Detect two consecutive `1`s in a bit stream (overlapping). Output `1` when detected.

### Mealy (outputs on edges, `input/output`)

```mermaid
stateDiagram-v2
    [*] --> S0
    S0 --> S0: 0 / 0
    S0 --> S1: 1 / 0
    S1 --> S0: 0 / 0
    S1 --> S1: 1 / 1
```

| State | Input | Next | Output |
|-------|-------|------|--------|
| S0 | 0 | S0 | 0 |
| S0 | 1 | S1 | 0 |
| S1 | 0 | S0 | 0 |
| S1 | 1 | S1 | 1 |

### Moore (outputs in states)

```mermaid
stateDiagram-v2
    [*] --> A
    A: A / out=0
    B: B / out=0
    C: C / out=1
    A --> A: 0
    A --> B: 1
    B --> A: 0
    B --> C: 1
    C --> A: 0
    C --> C: 1
```

| State | Output | Input 0 | Input 1 |
|-------|--------|---------|---------|
| A | 0 | A | B |
| B | 0 | A | C |
| C | 1 | A | C |

For input `0110111`: Mealy emits `0010011` immediately on the transition; Moore needs one extra state (C) and its output is observed after the transition, so the sequences match when read after each step.

## Properties to test
Both machines produce the same output stream for random bit strings.
