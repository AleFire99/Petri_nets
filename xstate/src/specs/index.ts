import type { AnyStateMachine } from 'xstate';
import { fillStationSpec } from './fillStation.checks';
import { doorAlarmSpec, philosophersSpec, vendingSpec } from './textbook.checks';
import type { MachineSpec } from './types';

type Spec = MachineSpec<AnyStateMachine>;

/** Register every machine here. Analyzer, tests and exporter iterate this list. */
export const specs: Spec[] = [
  fillStationSpec as Spec,
  doorAlarmSpec as Spec,
  vendingSpec as Spec,
  ...[2, 3, 4].flatMap((n) => [philosophersSpec(n, false), philosophersSpec(n, true)]),
];
