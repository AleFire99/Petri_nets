# Timed FSM

Transitions can fire automatically after a state has been active for a duration (timeout).

## Use case
Door alarm: if the door stays open for 30 s the alarm sounds.

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: open
    Open --> Closed: close
    Open --> Alarm: after 30s
    Alarm --> Closed: close
```

| From | Trigger | To |
|------|---------|----|
| Closed | open | Open |
| Open | close | Closed |
| Open | timeout 30 s | Alarm |
| Alarm | close | Closed |

The timer starts on entering `Open` and is cancelled on leaving it. Tests use a fake clock.

## Properties to test
No alarm at 29 s; alarm at 30 s; closing before 30 s cancels the timer; re-opening restarts the timer.
