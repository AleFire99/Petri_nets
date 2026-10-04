# Workflow nets (WF-nets) and soundness

A WF-net has a single source place `i`, a single sink place `o`, and every node lies on a path from `i` to `o`. It is **sound** if (1) from every reachable marking, the final marking `[o]` is reachable (option to complete), (2) whenever `o` is marked, nothing else is (proper completion), (3) no transition is dead.

## Sound: parallel review
`register` splits (AND) into two checks, `decide` joins.

```mermaid
flowchart LR
    i(("i (1)")) --> register["register"]
    register --> a(("a"))
    register --> b(("b"))
    a --> checkA["checkA"]
    b --> checkB["checkB"]
    checkA --> a2(("a2"))
    checkB --> b2(("b2"))
    a2 --> decide["decide"]
    b2 --> decide
    decide --> o(("o"))
    classDef trans fill:#333,stroke:#333,color:#fff
    class register,checkA,checkB,decide trans
```

## Unsound: XOR split feeding an AND join
Two alternative transitions choose one branch, but `join` needs both.

```mermaid
flowchart LR
    i(("i (1)")) --> chooseA["chooseA"]
    i --> chooseB["chooseB"]
    chooseA --> pa(("pa"))
    chooseB --> pb(("pb"))
    pa --> join["join"]
    pb --> join
    join --> o(("o"))
    classDef trans fill:#333,stroke:#333,color:#fff
    class chooseA,chooseB,join trans
```

After `chooseA` the marking `[pa]` is dead and `o` is unreachable: **deadlock**, option-to-complete violated, `join` is dead.

| Net | Sound | Reason |
|-----|-------|--------|
| Parallel review | yes | every reachable marking can reach `[o]`; no leftovers |
| XOR/AND mismatch | no | dead marking `[pa]`/`[pb]`, dead transition `join` |
