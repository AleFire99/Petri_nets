import { assign, setup } from 'xstate';

/**
 * Fill station: fill tank -> heat -> settle -> drain.
 *
 * EFSM features shown:
 *  - hierarchical states   (running.filling, running.heating, ...)
 *  - timed transitions     (`after`: settle time, fill/heat timeouts)
 *  - guards                (retry budget)
 *  - context variables     (retries, lastFault)
 *  - Moore outputs as tags (INLET, HEATER, OUTLET) -> map 1:1 to PLC outputs
 *
 * Keep this file literal (no helper functions building config) so the
 * VS Code visual editor and Stately Studio can parse it.
 */

export const TIMING = {
  FILL_TIMEOUT: 30_000,
  HEAT_TIMEOUT: 60_000,
  SETTLE_TIME: 5_000,
} as const;

export const MAX_RETRIES = 2;

export type FillStationEvent =
  | { type: 'START' }
  | { type: 'STOP' }
  | { type: 'ESTOP' }
  | { type: 'ESTOP_RELEASE' }
  | { type: 'RESET' }
  | { type: 'MAINT_RESET' }
  | { type: 'LEVEL_HIGH' }
  | { type: 'LEVEL_LOW' }
  | { type: 'TEMP_OK' };

export type FillStationContext = {
  retries: number;
  lastFault: null | 'FILL_TIMEOUT' | 'HEAT_TIMEOUT';
};

export const fillStation = setup({
  types: {
    context: {} as FillStationContext,
    events: {} as FillStationEvent,
  },
  delays: {
    FILL_TIMEOUT: TIMING.FILL_TIMEOUT,
    HEAT_TIMEOUT: TIMING.HEAT_TIMEOUT,
    SETTLE_TIME: TIMING.SETTLE_TIME,
  },
  guards: {
    canRetry: ({ context }) => context.retries < MAX_RETRIES,
  },
  actions: {
    setFault: assign({
      lastFault: (_, params: { code: FillStationContext['lastFault'] }) => params.code,
    }),
    countRetry: assign({ retries: ({ context }) => context.retries + 1 }),
    clearFaults: assign({ retries: 0, lastFault: null }),
  },
}).createMachine({
  id: 'fillStation',
  initial: 'idle',
  context: { retries: 0, lastFault: null },
  on: {
    ESTOP: { target: '.emergency' },
  },
  states: {
    idle: {
      on: { START: { target: 'running' } },
    },
    running: {
      initial: 'filling',
      on: { STOP: { target: 'idle' } },
      states: {
        filling: {
          tags: ['INLET'],
          on: { LEVEL_HIGH: { target: 'heating' } },
          after: {
            FILL_TIMEOUT: {
              target: '#fillStation.fault',
              actions: { type: 'setFault', params: { code: 'FILL_TIMEOUT' } },
            },
          },
        },
        heating: {
          tags: ['HEATER'],
          on: { TEMP_OK: { target: 'settling' } },
          after: {
            HEAT_TIMEOUT: {
              target: '#fillStation.fault',
              actions: { type: 'setFault', params: { code: 'HEAT_TIMEOUT' } },
            },
          },
        },
        settling: {
          after: { SETTLE_TIME: { target: 'draining' } },
        },
        draining: {
          tags: ['OUTLET'],
          on: { LEVEL_LOW: { target: '#fillStation.idle' } },
        },
      },
    },
    fault: {
      on: {
        RESET: [
          { guard: 'canRetry', target: 'idle', actions: 'countRetry' },
          { target: 'lockedOut' },
        ],
      },
    },
    lockedOut: {
      description: 'Retry budget used. Needs maintenance reset.',
      on: { MAINT_RESET: { target: 'idle', actions: 'clearFaults' } },
    },
    emergency: {
      on: { ESTOP_RELEASE: { target: 'idle' } },
    },
  },
});
