import { assign, setup } from 'xstate';

/**
 * Moore vs Mealy: detect "11" in a bit stream. Design: docs/fsm/moore-mealy.md.
 *
 * Both detectors run as parallel regions of ONE machine and see the same bits.
 *   mealy: output written by the transition (context.mealyOut)
 *   moore: output is a property of the state (tag OUT on state c)
 * The spec invariant "outputs agree" is checked in every reachable product
 * state. The product is finite, so this is an exact equivalence proof.
 */
export type Bit = { type: 'zero' } | { type: 'one' };

export const elevenDetector = setup({
  types: { context: {} as { mealyOut: 0 | 1 }, events: {} as Bit },
  actions: {
    emit: assign({ mealyOut: (_, p: { out: 0 | 1 }) => p.out }),
  },
}).createMachine({
  id: 'elevenDetector',
  type: 'parallel',
  context: { mealyOut: 0 },
  states: {
    mealy: {
      initial: 's0',
      states: {
        s0: {
          on: {
            zero: { target: 's0', actions: { type: 'emit', params: { out: 0 } } },
            one: { target: 's1', actions: { type: 'emit', params: { out: 0 } } },
          },
        },
        s1: {
          on: {
            zero: { target: 's0', actions: { type: 'emit', params: { out: 0 } } },
            one: { target: 's1', actions: { type: 'emit', params: { out: 1 } } },
          },
        },
      },
    },
    moore: {
      initial: 'a',
      states: {
        a: { on: { zero: { target: 'a' }, one: { target: 'b' } } },
        b: { on: { zero: { target: 'a' }, one: { target: 'c' } } },
        c: { tags: ['OUT'], on: { zero: { target: 'a' }, one: { target: 'c' } } },
      },
    },
  },
});
