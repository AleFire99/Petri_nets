import { setup } from 'xstate';

/**
 * FSM with history: washing machine. Design: docs/fsm/history.md.
 * `input.history` selects what `resume` restores:
 *   deep    -> exact leaf (wash.agitate)
 *   shallow -> direct child of running, entered at its default (wash.soak)
 *   none    -> running's initial state (fill)
 */
export type HistoryKind = 'deep' | 'shallow' | 'none';

export const washer = setup({
  types: {
    context: {} as { history: HistoryKind },
    input: {} as { history: HistoryKind },
    events: {} as
      | { type: 'start' }
      | { type: 'filled' }
      | { type: 'soaked' }
      | { type: 'washed' }
      | { type: 'pause' }
      | { type: 'resume' }
      | { type: 'stop' },
  },
  guards: {
    deep: ({ context }) => context.history === 'deep',
    shallow: ({ context }) => context.history === 'shallow',
  },
}).createMachine({
  id: 'washer',
  initial: 'off',
  context: ({ input }) => ({ history: input.history }),
  states: {
    off: { on: { start: { target: 'running' } } },
    running: {
      initial: 'fill',
      on: { pause: { target: 'paused' }, stop: { target: 'off' } },
      states: {
        fill: { tags: ['VALVE'], on: { filled: { target: 'wash' } } },
        wash: {
          initial: 'soak',
          on: { washed: { target: 'spin' } },
          states: {
            soak: { on: { soaked: { target: 'agitate' } } },
            agitate: { tags: ['DRUM'] },
          },
        },
        spin: { tags: ['DRUM'] },
        deepHist: { type: 'history', history: 'deep' },
        shallowHist: { type: 'history', history: 'shallow' },
      },
    },
    paused: {
      on: {
        resume: [
          { guard: 'deep', target: 'running.deepHist' },
          { guard: 'shallow', target: 'running.shallowHist' },
          { target: 'running' },
        ],
        stop: { target: 'off' },
      },
    },
  },
});
