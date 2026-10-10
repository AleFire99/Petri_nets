import { setup } from 'xstate';

/** Hierarchical FSM: `power_off` declared once on the parent. Design: fsm/docs/hierarchical.md. */
export const mediaPlayer = setup({
  types: {
    events: {} as
      | { type: 'power_on' }
      | { type: 'power_off' }
      | { type: 'play' }
      | { type: 'pause' }
      | { type: 'stop' },
  },
}).createMachine({
  id: 'mediaPlayer',
  initial: 'off',
  states: {
    off: { on: { power_on: { target: 'on' } } },
    on: {
      initial: 'stopped',
      on: { power_off: { target: 'off' } },
      states: {
        stopped: { on: { play: { target: 'playing' } } },
        playing: { tags: ['AUDIO'], on: { pause: { target: 'paused' }, stop: { target: 'stopped' } } },
        paused: { on: { play: { target: 'playing' }, stop: { target: 'stopped' } } },
      },
    },
  },
});
