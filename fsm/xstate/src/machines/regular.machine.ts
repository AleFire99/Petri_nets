import { setup } from 'xstate';

/** Regular (flat) FSMs. Design: fsm/docs/regular.md. */

export const trafficLight = setup({
  types: { events: {} as { type: 'next' } },
}).createMachine({
  id: 'trafficLight',
  initial: 'red',
  states: {
    red: { tags: ['RED'], on: { next: { target: 'green' } } },
    green: { tags: ['GREEN'], on: { next: { target: 'yellow' } } },
    yellow: { tags: ['YELLOW'], on: { next: { target: 'red' } } },
  },
});

export const turnstile = setup({
  types: { events: {} as { type: 'coin' } | { type: 'push' } },
}).createMachine({
  id: 'turnstile',
  initial: 'locked',
  states: {
    locked: { on: { coin: { target: 'unlocked' }, push: { target: 'locked' } } },
    unlocked: { tags: ['RELEASE'], on: { push: { target: 'locked' }, coin: { target: 'unlocked' } } },
  },
});
