import { setup } from 'xstate';

/**
 * Door alarm. Same design as docs/fsm/timed.md and src/petrilab/fsm/timed.py (sismic).
 * State ids match the Python implementation so test vectors replay 1:1.
 */
export const DOOR_TIMEOUT_MS = 30_000;

export const doorAlarm = setup({
  types: {
    events: {} as { type: 'open' } | { type: 'close' },
  },
  delays: { TIMEOUT: DOOR_TIMEOUT_MS },
}).createMachine({
  id: 'doorAlarm',
  initial: 'closed',
  states: {
    closed: { on: { open: { target: 'open' } } },
    open: {
      on: { close: { target: 'closed' } },
      after: { TIMEOUT: { target: 'alarm' } },
    },
    alarm: {
      tags: ['SIREN'],
      on: { close: { target: 'closed' } },
    },
  },
});
