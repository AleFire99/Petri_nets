# philosophers n=4 naive (docs/petri/examples.md)

```mermaid
stateDiagram-v2
  state "philosophers4Naive" as philosophers4Naive {
    state "phil0" as philosophers4Naive_phil0 {
      state "think" as philosophers4Naive_phil0_think
      state "hasLeft" as philosophers4Naive_phil0_hasLeft
      state "eat / EAT0" as philosophers4Naive_phil0_eat
      [*] --> philosophers4Naive_phil0_think
      philosophers4Naive_phil0_think --> philosophers4Naive_phil0_hasLeft : takeLeft0 [forksFree]
      philosophers4Naive_phil0_hasLeft --> philosophers4Naive_phil0_eat : takeRight0 [forksFree]
      philosophers4Naive_phil0_eat --> philosophers4Naive_phil0_think : done0
    }
    --
    state "phil1" as philosophers4Naive_phil1 {
      state "think" as philosophers4Naive_phil1_think
      state "hasLeft" as philosophers4Naive_phil1_hasLeft
      state "eat / EAT1" as philosophers4Naive_phil1_eat
      [*] --> philosophers4Naive_phil1_think
      philosophers4Naive_phil1_think --> philosophers4Naive_phil1_hasLeft : takeLeft1 [forksFree]
      philosophers4Naive_phil1_hasLeft --> philosophers4Naive_phil1_eat : takeRight1 [forksFree]
      philosophers4Naive_phil1_eat --> philosophers4Naive_phil1_think : done1
    }
    --
    state "phil2" as philosophers4Naive_phil2 {
      state "think" as philosophers4Naive_phil2_think
      state "hasLeft" as philosophers4Naive_phil2_hasLeft
      state "eat / EAT2" as philosophers4Naive_phil2_eat
      [*] --> philosophers4Naive_phil2_think
      philosophers4Naive_phil2_think --> philosophers4Naive_phil2_hasLeft : takeLeft2 [forksFree]
      philosophers4Naive_phil2_hasLeft --> philosophers4Naive_phil2_eat : takeRight2 [forksFree]
      philosophers4Naive_phil2_eat --> philosophers4Naive_phil2_think : done2
    }
    --
    state "phil3" as philosophers4Naive_phil3 {
      state "think" as philosophers4Naive_phil3_think
      state "hasLeft" as philosophers4Naive_phil3_hasLeft
      state "eat / EAT3" as philosophers4Naive_phil3_eat
      [*] --> philosophers4Naive_phil3_think
      philosophers4Naive_phil3_think --> philosophers4Naive_phil3_hasLeft : takeLeft3 [forksFree]
      philosophers4Naive_phil3_hasLeft --> philosophers4Naive_phil3_eat : takeRight3 [forksFree]
      philosophers4Naive_phil3_eat --> philosophers4Naive_phil3_think : done3
    }
  }
  [*] --> philosophers4Naive
```
