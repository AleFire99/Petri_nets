# Regular FSM

A flat, deterministic machine: a finite set of states, one active at a time, and a transition function `(state, event) -> state`. Events with no matching transition are invalid.

## Use case
Traffic light (cyclic) and turnstile (event-driven, with self-loops).

## Traffic light

```mermaid
stateDiagram-v2
    [*] --> Red
    Red --> Green: next
    Green --> Yellow: next
    Yellow --> Red: next
```

| From | Event | To |
|------|-------|----|
| Red | next | Green |
| Green | next | Yellow |
| Yellow | next | Red |

## Turnstile

```mermaid
stateDiagram-v2
    [*] --> Locked
    Locked --> Unlocked: coin
    Locked --> Locked: push
    Unlocked --> Locked: push
    Unlocked --> Unlocked: coin
```

| From | Event | To |
|------|-------|----|
| Locked | coin | Unlocked |
| Locked | push | Locked |
| Unlocked | push | Locked |
| Unlocked | coin | Unlocked |

## Properties to test
Every listed transition works; any other `(state, event)` pair is rejected (traffic light has only `next`, so every pair is valid).
