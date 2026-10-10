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
  /** @xstate-layout N4IgpgJg5mDOIC5QDMCWAbdBlALgQx1QHsA7AYgFEsAVAeQAUBtABgF1FQAHI2VQ0jiAAeiACwAmADQgAnogBsAdkUA6UYvkBWAIybNAZi0AOcZoC+Z6Wky4CxEitQR0YMjQCCAJWot2SENy8-CSCIgjaUrKIERZWGNj4wSoATgCuJCSoJFBudExsgoF89qHRzIraKprypprl4szy+uJG0nIIDeIq4qIAnP1K8toSvTGWINYJdqQp6ZnZKpNZOQAyFABqFCsA+gASAJIA4ru+hTzFAv5hDb0qzPfM2swD4r2vvW2I4soq2vL-8iMzH0onkjXE+liE3itiSaQyy0W8WWZCEsESYBUeGQODAyQAFAAxfYrHbUfYAWQotAAqtQAJRkSaw+yzBELJbZU7+IrBUrhcqVaq1eqNZqtKIIURGTS-bS9RRGPr6Iy9ZjfKHMxKs+HzKAqAAWYDs2TI1AoFPo21oAGluVxznyrmIlSoZb19B7tDLnmrFJ8OopmCpFH1+spFANRqJNTDtTNdYijSacmiMVicXj8bsKO5qNtyVTaQymXHpg5Ewtk4QuQUeY6Ss6BUYhTU9KKmi0A56un9-ppeqCNKI9PJYzZ4xW5ojYGAcDh0Ci0wRMdjcQSsBRqNQ1gXKRRGVry2y9SpZ-PF7W-A6go3QGFQ8HxbojPpns0+gHvl0ev0FcxNCBVUjHHKY4WnBYIGSPAshRNZNh2FZaAAdXtAIG0ue8ygqKo2zqRQGk7CV2m+YNQz-CMo2GUCWRmZA8FSdAcDITwqC3NDeTvYRok9YMdGqGVFAHUx9E0btRjUP8PU0cQWkAiEaMnRYGKYli2J8bRr3Q29MO48JeKqXRAU0IS3gMMTJVHENxC0eVI0MD1IXGI8knQIgAGMAGtIFoVJmIpdx9gAOXzVjNx8OsbwuEImxqANtAiWU1TqNUngVDRFEU48wAAWzxGASHcmRKBoBhtlYtZ3E3DiMJirCEBk+LZMqGUTGGbR9AIoSLHGEgiAgOBBBcrjON0sIAFpDADcahKqB4lQVTRRH0BLxCypInBcM4dLqvSISMFROrqcpGkjExvgDfp9BUBUtBO2TDEadadQgqBtui-lPXi19umO0YbO0RVekA56E1epFMGWd6nXqox-UlFpRDuV8QWaXo23KcxnLLcD2X1asofrHbPpqN0BxVcRvSMIEhi-H4AS0N8OsA0RmBjbGJ2PSt9XPBdCaimG9KGA7n3UFa3xWj4EZw39ehMITVVBQdQanPGVCgmC9WhriwmjXCRIVHp9E9YivhlsN5cAwd5GVjmwNZejGJwbWxuiGyDv4wFZMUEEKnkAMJEqYZmlEgCDBqXoVZUNyvJ8vyXd2sI-mGG6lWWoY+ghYYAwMJHbr0PRDDBUMo9y-KwEK9oBZ16Ilv1voloiJUlUidolFUW7RCeFVBw1HqgA */
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
