import { setup } from 'xstate';

/**
 * Door alarm. Same design as fsm/docs/timed.md and src/petrilab/fsm/timed.py (sismic).
 * State ids match the Python implementation so test vectors replay 1:1.
 */
export const DOOR_TIMEOUT_MS = 30_000;

export const doorAlarm = setup({
  types: {
    events: {} as { type: 'open' } | { type: 'close' },
  },
  delays: { TIMEOUT: DOOR_TIMEOUT_MS },
}).createMachine({
  /** @xstate-layout N4IgpgJg5mDOIC5QQPYoE4EEA2BDdAtgHQDG2KskAxCgA5gB2A2gAwC6iotFAlgC48UDTiAAeiAIwB2AJwAaEAE9EAJgCsKolLUBfHQtQYc+YnUZUyFMKw5IQ3WP0HC74hNPlLVLTer0G0LDxCIjMGKlFYPlw+MCJcADNY9AAKABUASQBZAFEAeQBVNIBKKkMgk1D6ZnYRBychETcAFh8iAA4Vdol1BWUEFQkJDoBmMfGJseb-EHLjENxgggtyShs63gFG10RmtRYiHrU+xG6iXRmGFAg4ETmljcctl1A3AFoANhOET6IWf-+zQkHyk3Q+EhkIwuASMS1Iq0gjwaLzEuxU3xkww+fn0s0C81M1SRzyaqnaB063V6XgGEgpkwZI2muPulUWJmJzlJCDUamGMjUIyOGIOLHajMmej0QA */
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
