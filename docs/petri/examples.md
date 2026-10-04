# Classic examples

## 1. Producer/consumer (bounded buffer, capacity 2)
`produce` needs a free slot and puts an item in the buffer; `consume` takes an item and frees the slot.

```mermaid
flowchart LR
    ProdIdle(("ProdIdle (1)")) --> produce["produce"]
    Free(("Free (2)")) --> produce
    produce --> ProdIdle
    produce --> Buffer(("Buffer (0)"))
    Buffer --> consume["consume"]
    ConsIdle(("ConsIdle (1)")) --> consume
    consume --> ConsIdle
    consume --> Free
    classDef trans fill:#333,stroke:#333,color:#fff
    class produce,consume trans
```

Places `(ProdIdle, Free, Buffer, ConsIdle)`; `produce`: pre (1,1,0,0) post (1,0,1,0); `consume`: pre (0,0,1,1) post (0,1,0,1).
- Bounded (2), live, deadlock-free; P-invariants: `Free + Buffer = 2`, `ProdIdle = 1`, `ConsIdle = 1`.

## 2. Dining philosophers (n = 2 shown; implemented for any n)
Each philosopher `i` has `Think_i (1)`, `HasLeft_i`, `Eat_i`; forks `Fork_i (1)`; philosopher `i` takes left fork `Fork_i`, then right fork `Fork_{(i+1) mod n}`.

```mermaid
flowchart LR
    T0(("Think0 (1)")) --> L0["takeLeft0"]
    F0(("Fork0 (1)")) --> L0
    L0 --> HL0(("HasLeft0"))
    HL0 --> R0["takeRight0"]
    F1(("Fork1 (1)")) --> R0
    R0 --> E0(("Eat0"))
    E0 --> D0["done0"]
    D0 --> T0
    D0 --> F0
    D0 --> F1
    T1(("Think1 (1)")) --> L1["takeLeft1"]
    F1 --> L1
    L1 --> HL1(("HasLeft1"))
    HL1 --> R1["takeRight1"]
    F0 --> R1
    R1 --> E1(("Eat1"))
    E1 --> D1["done1"]
    D1 --> T1
    D1 --> F0
    D1 --> F1
    classDef trans fill:#333,stroke:#333,color:#fff
    class L0,R0,D0,L1,R1,D1 trans
```

**Deadlock**: both take their left fork -> marking `HasLeft0 = HasLeft1 = 1`, all forks taken, nothing enabled.

**Fix (atomic pickup)**: replace `takeLeft_i` and `takeRight_i` by a single transition `take_i` consuming `Think_i`, `Fork_i`, `Fork_{i+1}` and producing `Eat_i`. No dead marking exists; the net is deadlock-free and live. Invariant: `Fork_i + Eat_i + Eat_{i-1} = 1`.

## 3. Mutual exclusion
Two processes share a `Mutex (1)`. Per process `k`: `Idle_k (1)`, `Wait_k`, `Crit_k`; transitions `request_k` (Idle -> Wait), `enter_k` (Wait + Mutex -> Crit), `leave_k` (Crit -> Idle + Mutex).

```mermaid
flowchart LR
    I1(("Idle1 (1)")) --> req1["request1"]
    req1 --> W1(("Wait1"))
    W1 --> enter1["enter1"]
    M(("Mutex (1)")) --> enter1
    enter1 --> C1(("Crit1"))
    C1 --> leave1["leave1"]
    leave1 --> I1
    leave1 --> M
    I2(("Idle2 (1)")) --> req2["request2"]
    req2 --> W2(("Wait2"))
    W2 --> enter2["enter2"]
    M --> enter2
    enter2 --> C2(("Crit2"))
    C2 --> leave2["leave2"]
    leave2 --> I2
    leave2 --> M
    classDef trans fill:#333,stroke:#333,color:#fff
    class req1,enter1,leave1,req2,enter2,leave2 trans
```

Safety: `Crit1 + Crit2 <= 1` in every reachable marking (follows from invariant `Mutex + Crit1 + Crit2 = 1`). Deadlock-free and live. Marking count: 8.

## 4. Traffic lights for a crossing
Two roads share a `Safe` token: a road may turn green only by taking `Safe`, and returns it when turning red. Initial `NS_Red = EW_Red = Safe = 1`.

```mermaid
flowchart LR
    NSR(("NS_Red (1)")) --> nsGo["nsGo"]
    Tok(("Safe (1)")) --> nsGo
    nsGo --> NSG(("NS_Green"))
    NSG --> nsStop["nsStop"]
    nsStop --> NSR
    nsStop --> Tok
    EWR(("EW_Red (1)")) --> ewGo["ewGo"]
    Tok --> ewGo
    ewGo --> EWG(("EW_Green"))
    EWG --> ewStop["ewStop"]
    ewStop --> EWR
    ewStop --> Tok
    classDef trans fill:#333,stroke:#333,color:#fff
    class nsGo,nsStop,ewGo,ewStop trans
```

Safety: `NS_Green + EW_Green <= 1` (invariant `Safe + NS_Green + EW_Green = 1`). 3 reachable markings, live, deadlock-free.
