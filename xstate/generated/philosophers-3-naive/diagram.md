# philosophers n=3 naive (docs/petri/examples.md)

```mermaid
stateDiagram-v2
  state "philosophers3Naive" as philosophers3Naive {
    state "phil0" as philosophers3Naive_phil0 {
      state "think" as philosophers3Naive_phil0_think
      state "hasLeft" as philosophers3Naive_phil0_hasLeft
      state "eat / EAT0" as philosophers3Naive_phil0_eat
      [*] --> philosophers3Naive_phil0_think
      philosophers3Naive_phil0_think --> philosophers3Naive_phil0_hasLeft : takeLeft0 [forksFree]
      philosophers3Naive_phil0_hasLeft --> philosophers3Naive_phil0_eat : takeRight0 [forksFree]
      philosophers3Naive_phil0_eat --> philosophers3Naive_phil0_think : done0
    }
    --
    state "phil1" as philosophers3Naive_phil1 {
      state "think" as philosophers3Naive_phil1_think
      state "hasLeft" as philosophers3Naive_phil1_hasLeft
      state "eat / EAT1" as philosophers3Naive_phil1_eat
      [*] --> philosophers3Naive_phil1_think
      philosophers3Naive_phil1_think --> philosophers3Naive_phil1_hasLeft : takeLeft1 [forksFree]
      philosophers3Naive_phil1_hasLeft --> philosophers3Naive_phil1_eat : takeRight1 [forksFree]
      philosophers3Naive_phil1_eat --> philosophers3Naive_phil1_think : done1
    }
    --
    state "phil2" as philosophers3Naive_phil2 {
      state "think" as philosophers3Naive_phil2_think
      state "hasLeft" as philosophers3Naive_phil2_hasLeft
      state "eat / EAT2" as philosophers3Naive_phil2_eat
      [*] --> philosophers3Naive_phil2_think
      philosophers3Naive_phil2_think --> philosophers3Naive_phil2_hasLeft : takeLeft2 [forksFree]
      philosophers3Naive_phil2_hasLeft --> philosophers3Naive_phil2_eat : takeRight2 [forksFree]
      philosophers3Naive_phil2_eat --> philosophers3Naive_phil2_think : done2
    }
  }
  [*] --> philosophers3Naive
```
