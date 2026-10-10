import { assign, setup } from 'xstate';

/**
 * Moore vs Mealy: detect "11" in a bit stream. Design: fsm/docs/moore-mealy.md.
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
  /** @xstate-layout N4IgpgJg5mDOIC5RgDZgG5gHYBEwBcwBjfAewCcA6AWzAEMUBPS2ABgGIAvMc0gbVYBdRKAAOpWAEt8k0lhEgAHogAcAdkoAWTQFYAzAEZDOtWoCcZtXoA0IRogMA2A5QOa9AJh0e1Ov2b09FQBfYNtUDGw8QhIKGnomFg45MAFhJBBxKRk5BWUED1ZNSlZS0s9NVg8jS1t7As1HSjN9I08vZzUPUPC0TFwCYjIqWgZmWAMuHn4hBSzpWXkM-MLisvKPSuq9WrsHHRd1gz9fPU0DLx7wPqjB2JGE8cmUtLmJBdzlxE9WSj9GgLtRweFQeOoONQuLqOHSOFQqPSOYEeQJXCL9aJDOLUUgUMCUOhTXivDLzHJLUD5AIlAK+AwWFoqHSsAzghB+JqtDxw5ysHTwnRom4DGLDGi48j4wkvWak97kvKIaprdYVKo1NRs4F6Sgw4Gg7xVPSsEJha6REVYkYS-EAIyJM3SYnli0VBTcJVVm3VO01e3ZVlcsJ8NS8TjMQotmPu4rxlHtMqdmRdn0piHcvxUF2ZJmVkLMWoMKhKXTMmis7TUTMjGLuYpxcaIDpJzuyrq+CAzlCzXj5XTc+bZug8WlYwJhoJUSJrt1F2JtlCbibebdTSkQOncut7rACPkcRUcbNhOj+pccminmjLllCZqwpAgcAU6NnVpXHwp64QAFp6Wyf02T11hA0o3BnS0Y1GJgPwVDsPALf1HB1Zl1mREx3EFM1X0g+tHiSWD2zTBBTDZbkR13ZC1CKPkpwCCDozwsYWAMQi13yQxfgMXcghZC9Jx0Miul1cweUvOEzARBi63nPE2K-FZEPqRFijMMde3UfkAnA7DhUY2TJQJeS3VIpCLhKQwfEsIJjU2aS52tONbWMjtjWLHtmU2DzzELYtczLCsPB8atdKjGTHMMogXOI7xT2BVDr3i44VC1aoSwQ3wLG5ZCsNCIA */
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
