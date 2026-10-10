import type { AnyStateMachine } from 'xstate';
import { designSpecs } from './designs.checks';
import { fillStationSpec } from './fillStation.checks';
import { philosophers2Specs, philosophersSpec } from './philosophers.checks';
import type { MachineSpec } from './types';

type Spec = MachineSpec<AnyStateMachine>;

/** Register every machine here. Analyzer, tests and exporter iterate this list. */
export const specs: Spec[] = [
  ...designSpecs,
  fillStationSpec as Spec,
  ...philosophers2Specs,
  ...[2, 3, 4].flatMap((n) => [philosophersSpec(n, false), philosophersSpec(n, true)]),
];
