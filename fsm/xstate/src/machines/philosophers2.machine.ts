import { assign, setup } from 'xstate';

/**
 * Dining philosophers, n = 2, written out literally so the VS Code visual editor
 * can open it (the n-ary factory in philosophers.machine.ts cannot be parsed).
 * Forks are context booleans (true = on the table). Fork 0 and fork 1 are each
 * philosopher's left or right: phil0 uses (0, 1), phil1 uses (1, 0).
 * test/philosophers2.test.ts proves both machines have the same state space as
 * createPhilosophers(2, ...).
 */
type Ctx = { forks: boolean[] };
type Params = { forks: number[] };

const setForks = (ctx: Ctx, forks: number[], value: boolean) =>
  ctx.forks.map((v, f) => (forks.includes(f) ? value : v));

/** Deadlock-free: each philosopher takes both forks in one step. */
export const philosophers2Atomic = setup({
  types: { context: {} as Ctx, events: {} as { type: string } },
  guards: {
    forksFree: ({ context }, p: Params) => p.forks.every((f) => context.forks[f]),
  },
  actions: {
    takeForks: assign({ forks: ({ context }, p: Params) => setForks(context, p.forks, false) }),
    putForks: assign({ forks: ({ context }, p: Params) => setForks(context, p.forks, true) }),
  },
}).createMachine({
  id: 'philosophers2Atomic',
  type: 'parallel',
  context: { forks: [true, true] },
  states: {
    phil0: {
      initial: 'think',
      states: {
        think: {
          on: {
            take0: {
              guard: { type: 'forksFree', params: { forks: [0, 1] } },
              actions: { type: 'takeForks', params: { forks: [0, 1] } },
              target: 'eat',
            },
          },
        },
        eat: {
          tags: ['EAT0'],
          on: { done0: { actions: { type: 'putForks', params: { forks: [0, 1] } }, target: 'think' } },
        },
      },
    },
    phil1: {
      initial: 'think',
      states: {
        think: {
          on: {
            take1: {
              guard: { type: 'forksFree', params: { forks: [1, 0] } },
              actions: { type: 'takeForks', params: { forks: [1, 0] } },
              target: 'eat',
            },
          },
        },
        eat: {
          tags: ['EAT1'],
          on: { done1: { actions: { type: 'putForks', params: { forks: [1, 0] } }, target: 'think' } },
        },
      },
    },
  },
});

/** Can deadlock: both take their left fork, then wait forever for the right one. */
export const philosophers2Naive = setup({
  types: { context: {} as Ctx, events: {} as { type: string } },
  guards: {
    forksFree: ({ context }, p: Params) => p.forks.every((f) => context.forks[f]),
  },
  actions: {
    takeForks: assign({ forks: ({ context }, p: Params) => setForks(context, p.forks, false) }),
    putForks: assign({ forks: ({ context }, p: Params) => setForks(context, p.forks, true) }),
  },
}).createMachine({
  /** @xstate-layout N4IgpgJg5mDOIC5QAcAWBLANge1ttYATrAEwByAhugG5gB0aWADHQC4YB2A1gMSsVcwAGTAAzVkwDaTALqIUudK3TYO8kAA9EARgCcugDQgAnohK6ALHQsB2AGy3bADhtMb2uwFYAvt6OMcPAJicipaBgxMFlQKWBFxPgEwACV0KFQJaTkkEGRFZVV1LQRPCwBmOl1PMu0STyNTBHMrWwcbZ1d3L19-SNx8VCJSShp6AJYwClYeCFUwKVl1PNglFTUc4ocWuxd6kx1PFn19WpIXNw8fP1y+oMGQkfCA7TZOXn5BeNZtLKX8taKOn0DUQDgqFiYdhIbhIdiYThINhIPRuWH6wWGYTGkReMTiYmmHxSaQyP0WOWWq0KG0QpRe2k8UL2jTB1kh0KRcIRSJRAXR90xowiWBek2msw4YDJ2QUKwK61AmzKTjouxBCAs+kq5i29nhiORKI42AgcCWtwGQ1Coz+coBNIQAFoSBZ1c6KsdPV7dE5eRaMdanpEmLaqQrNGZXfsEHZwcdGdpytVPE4yn60XcrY9scxXuhuKH5YCEEj1dobLpVUwffDakwIZqbOnApaHljhVE6HivoX7YrEBYSC8qjU6uqajY6K4ykwykjzl0rr0M63BUHc2Le9T+yX7HRtNW58ydAi6DOa046w3dE3rnzM22hc8t+Hii71RZatZzJ59DYF5czb8lm7bPHmBYUv824RiWJDqp4ZxTmUVQQr+n5wkuqItgG2YdrisQ9pBdrQcUn6VgyTLqnY1F0LGiJ2DeXIGkBD5rjmmCilML7FjYrh0J4FFjtG1QvCQyGlEwaEeJJvi+EAA */
  id: 'philosophers2Naive',
  type: 'parallel',
  context: { forks: [true, true] },
  states: {
    phil0: {
      initial: 'think',
      states: {
        think: {
          on: {
            takeLeft0: {
              guard: { type: 'forksFree', params: { forks: [0] } },
              actions: { type: 'takeForks', params: { forks: [0] } },
              target: 'hasLeft',
            },
          },
        },
        hasLeft: {
          on: {
            takeRight0: {
              guard: { type: 'forksFree', params: { forks: [1] } },
              actions: { type: 'takeForks', params: { forks: [1] } },
              target: 'eat',
            },
          },
        },
        eat: {
          tags: ['EAT0'],
          on: { done0: { actions: { type: 'putForks', params: { forks: [0, 1] } }, target: 'think' } },
        },
      },
    },
    phil1: {
      initial: 'think',
      states: {
        think: {
          on: {
            takeLeft1: {
              guard: { type: 'forksFree', params: { forks: [1] } },
              actions: { type: 'takeForks', params: { forks: [1] } },
              target: 'hasLeft',
            },
          },
        },
        hasLeft: {
          on: {
            takeRight1: {
              guard: { type: 'forksFree', params: { forks: [0] } },
              actions: { type: 'takeForks', params: { forks: [0] } },
              target: 'eat',
            },
          },
        },
        eat: {
          tags: ['EAT1'],
          on: { done1: { actions: { type: 'putForks', params: { forks: [1, 0] } }, target: 'think' } },
        },
      },
    },
  },
});
