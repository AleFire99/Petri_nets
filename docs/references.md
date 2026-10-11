# References

Reading list behind the docs and the [study plan](../study-plan.md). ★ = start here.

## Petri nets

- ★ T. Murata, "Petri nets: Properties, analysis and applications", *Proceedings of the IEEE* 77(4), 541–580, 1989. [doi:10.1109/5.24143](https://doi.org/10.1109/5.24143). The standard survey: definitions, properties, liveness levels, invariants, subclasses. Notation used in [foundations.md](petri/foundations.md).
- ★ W. Reisig, *Understanding Petri Nets: Modeling Techniques, Analysis Methods, Case Studies*, Springer, 2013. Gentle textbook, many small examples.
- J. L. Peterson, *Petri Net Theory and the Modeling of Systems*, Prentice Hall, 1981. Classic introduction; reachability and coverability trees.
- J. Desel and J. Esparza, *Free Choice Petri Nets*, Cambridge University Press, 1995. Structure theory (siphons, traps, rank theorem).
- R. David and H. Alla, *Discrete, Continuous, and Hybrid Petri Nets*, 2nd ed., Springer, 2010. Timed and continuous nets, control engineering view.
- C. G. Cassandras and S. Lafortune, *Introduction to Discrete Event Systems*, 3rd ed., Springer, 2021. Automata and Petri nets side by side, supervisory control, stochastic models.
- R. M. Karp and R. E. Miller, "Parallel program schemata", *Journal of Computer and System Sciences* 3(2), 147–195, 1969. Origin of the coverability tree ([coverability.md](petri/coverability.md)).
- J. Esparza and M. Nielsen, "Decidability issues for Petri nets: a survey", *Journal of Information Processing and Cybernetics (EIK)* 30(3), 1994. What is and is not decidable.
- W. M. P. van der Aalst, "The application of Petri nets to workflow management", *Journal of Circuits, Systems and Computers* 8(1), 21–66, 1998. Workflow nets and soundness ([workflow.md](petri/workflow.md)).
- C. A. Petri, *Kommunikation mit Automaten*, PhD thesis, Universität Bonn, 1962. The origin.

## Coloured Petri nets

- ★ K. Jensen and L. M. Kristensen, *Coloured Petri Nets: Modelling and Validation of Concurrent Systems*, Springer, 2009. Formal definition used in [cpn-formal.md](petri/cpn-formal.md), state spaces, timed CPNs, CPN Tools.
- K. Jensen, *Coloured Petri Nets: Basic Concepts, Analysis Methods and Practical Use*, vols. 1–3, Springer, 1992–1997. The original monographs.
- L. M. Kristensen, S. Christensen and K. Jensen, "The practitioner's guide to coloured Petri nets", *International Journal on Software Tools for Technology Transfer* 2(2), 98–132, 1998. Practical modelling with CPN Tools.

## FSMs, EFSMs, statecharts, testing

- ★ K.-T. Cheng and A. S. Krishnakumar, "Automatic functional test generation using the extended finite state machine model", *Proc. 30th Design Automation Conference (DAC)*, 86–91, 1993. EFSM definition used in [efsm-formal.md](fsm/efsm-formal.md).
- ★ D. Lee and M. Yannakakis, "Principles and methods of testing finite state machines: a survey", *Proceedings of the IEEE* 84(8), 1090–1123, 1996. Conformance testing, checking sequences.
- T. S. Chow, "Testing software design modeled by finite-state machines", *IEEE Transactions on Software Engineering* SE-4(3), 178–187, 1978. The W-method.
- D. Harel, "Statecharts: A visual formalism for complex systems", *Science of Computer Programming* 8(3), 231–274, 1987. Hierarchy, orthogonality, history: the semantics XState implements.
- C. Baier and J.-P. Katoen, *Principles of Model Checking*, MIT Press, 2008. Transition systems, invariants, state-space exploration, LTL/CTL.

## Tools and online resources

- [CPN Tools](https://cpntools.org/): editor, simulator and state-space analyser for CPNs.
- [Petri Nets World](https://www.informatik.uni-hamburg.de/TGI/PetriNets/): community portal, tool database, bibliography.
- [SNAKES](https://github.com/fpom/snakes) (used here) and [PM4Py](https://pm4py.fit.fraunhofer.de/) (soundness cross-check): see [library-evaluation.md](petri/library-evaluation.md).
- [XState v5 documentation](https://stately.ai/docs/xstate): machines, guards, context, `transition()` for pure stepping.
- [pytest](https://docs.pytest.org/), [Hypothesis](https://hypothesis.readthedocs.io/) (property-based testing), [uv](https://docs.astral.sh/uv/).
