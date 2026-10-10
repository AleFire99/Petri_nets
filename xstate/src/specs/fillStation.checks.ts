import { fillStation, type FillStationEvent } from '../machines/fillStation.machine';
import type { MachineSpec } from './types';

/**
 * Verification spec: what the environment can do, what "home" means,
 * what must never happen. Used by analyzer, tests and test-vector export.
 */
export const fillStationSpec: MachineSpec<typeof fillStation> = {
  slug: 'fill-station',
  name: 'fillStation',
  machine: fillStation,
  events: (
    ['START', 'STOP', 'ESTOP', 'ESTOP_RELEASE', 'RESET', 'MAINT_RESET',
     'LEVEL_HIGH', 'LEVEL_LOW', 'TEMP_OK'] as FillStationEvent['type'][]
  ).map((type) => ({ type }) as FillStationEvent),
  marked: (s) => s.matches('idle'),
  invariants: {
    'inlet and outlet never open together': (s) => !(s.hasTag('INLET') && s.hasTag('OUTLET')),
    'heater only with valves closed': (s) =>
      !s.hasTag('HEATER') || (!s.hasTag('INLET') && !s.hasTag('OUTLET')),
    'no outputs in emergency': (s) =>
      !s.matches('emergency') || (!s.hasTag('INLET') && !s.hasTag('HEATER') && !s.hasTag('OUTLET')),
    'retry counter bounded': (s) => s.context.retries <= 2,
  },
  expect: { deadlocks: 0, blocking: 0 },
  vectors: true, // replayed by tests/fsm/test_fill_station.py
  codegen: { st: true },
};
