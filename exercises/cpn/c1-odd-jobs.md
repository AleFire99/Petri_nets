# C1 · Guards and bindings (beginner)

**Goal:** compute bindings, enabling and the occurrence graph of a small CPN.
**Read first:** [CPN formal](../../docs/petri/cpn-formal.md) sections 1–3, [coloured net](../../docs/petri/colored.md); run `examples/cpn_bindings_and_unfolding.py`.

Jobs `{1, 2, 3, 4, 5}` (colour set `JOB = 0..9`). Transition `square` takes a job `n` **only if `n` is odd** and puts `n*n` in `Results`.

1. Write the colour sets, the variable, the guard and both arc expressions.
2. Which bindings of `square` are enabled in `M0`? Why are the others not?
3. Predict the number of reachable markings and edges before computing them.
4. Which markings are dead? Are they empty?
5. Show three invalid cases: a binding failing the guard, a binding without a token, an initial token outside the colour set.
6. Edge case: jobs `(3, 3)`. What do the markings look like in multiset notation?

**Check yourself:** 8 markings. Solution: [`c1_odd_jobs.py`](../solutions/c1_odd_jobs.py).
