# FSM designs

Each design is a Markdown file with a description, use case, a Mermaid `stateDiagram-v2` and a transition table. Later phases implement every design in `src/petrilab/fsm/`.

| # | Design | Variant | Example |
|---|--------|---------|---------|
| 1 | [Regular](regular.md) | flat, deterministic | traffic light, turnstile |
| 2 | [Hierarchical](hierarchical.md) | nested states | media player |
| 3 | [Extended](extended.md) | guards + context variables | vending machine |
| 4 | [Timed](timed.md) | timeouts | door alarm |
| 5 | [History](history.md) | shallow / deep history | washing machine |
| 6 | [Parallel](parallel.md) | orthogonal regions | text styling |
| 7 | [Moore vs Mealy](moore-mealy.md) | output models | "11" detector |

Next: [library evaluation](library-evaluation.md) (spikes in `spikes/fsm/`).
