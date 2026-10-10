# philosophers n=2 atomic (docs/petri/examples.md)

```mermaid
stateDiagram-v2
  state "philosophers2Atomic" as philosophers2Atomic {
    state "phil0" as philosophers2Atomic_phil0 {
      state "think" as philosophers2Atomic_phil0_think
      state "eat / EAT0" as philosophers2Atomic_phil0_eat
      [*] --> philosophers2Atomic_phil0_think
      philosophers2Atomic_phil0_think --> philosophers2Atomic_phil0_eat : take0 [forksFree]
      philosophers2Atomic_phil0_eat --> philosophers2Atomic_phil0_think : done0
    }
    --
    state "phil1" as philosophers2Atomic_phil1 {
      state "think" as philosophers2Atomic_phil1_think
      state "eat / EAT1" as philosophers2Atomic_phil1_eat
      [*] --> philosophers2Atomic_phil1_think
      philosophers2Atomic_phil1_think --> philosophers2Atomic_phil1_eat : take1 [forksFree]
      philosophers2Atomic_phil1_eat --> philosophers2Atomic_phil1_think : done1
    }
  }
  [*] --> philosophers2Atomic
```
