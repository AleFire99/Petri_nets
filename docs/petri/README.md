# Petri net designs

## Notation in the Mermaid diagrams
- **Place**: circle, label `name (tokens)` shows the initial marking.
- **Transition**: dark rectangle (bar).
- **Arc**: `-->` (label = weight when > 1). **Inhibitor arc**: `--o` (enables only if the place has fewer than `weight` tokens). **Read (test) arc**: dotted `-.-` (needs tokens but does not consume).
- Marking `M` is written as a vector over the places listed in each document.

Firing rule: a transition is enabled in `M` if every input place has at least the arc weight in tokens (plus inhibitor/read conditions); firing removes input tokens and adds output tokens.

| # | Design | Variant | Verified property |
|---|--------|---------|-------------------|
| 1 | [Place/transition net](place-transition.md) | weights, conservation | reachability, boundedness, invariants |
| 2 | [Inhibitor & read arcs](inhibitor-read.md) | extended arcs | boundedness via inhibitor |
| 3 | [Coloured net](colored.md) | typed tokens + guards | guard blocks transition |
| 4 | [Timed net](timed.md) | firing intervals | timeout transition never fires |
| 5 | [Stochastic net](stochastic.md) | exponential rates | steady-state vs analytic M/M/1/K |
| 6 | [Hierarchical net](hierarchical.md) | substitution transition | flattening equals expected net |
| 7 | [Workflow nets](workflow.md) | WF-net soundness | sound vs unsound |
| 8 | [Classic examples](examples.md) | producer/consumer, philosophers, mutex, traffic | deadlock freedom, invariants |

Next: [library evaluation](library-evaluation.md).
