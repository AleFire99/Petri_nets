import type { AnyStateMachine } from 'xstate';
import { doorAlarm } from '../machines/doorAlarm.machine';
import { createPhilosophers, philosopherEvents } from '../machines/philosophers.machine';
import { type VendingEvent, vendingMachine } from '../machines/vendingMachine.machine';
import type { MachineSpec } from './types';

/** XState ports of designs that already exist in docs/fsm and docs/petri. */

export const doorAlarmSpec: MachineSpec<typeof doorAlarm> = {
  slug: 'door-alarm',
  name: 'doorAlarm (docs/fsm/timed.md)',
  machine: doorAlarm,
  events: [{ type: 'open' }, { type: 'close' }],
  marked: (s) => s.matches('closed'),
  invariants: { 'siren only in alarm': (s) => s.hasTag('SIREN') === s.matches('alarm') },
  expect: { deadlocks: 0, blocking: 0 },
};

const coins: VendingEvent[] = [0, 25, 50, 100].map((amount) => ({ type: 'insert', amount }));

export const vendingSpec: MachineSpec<typeof vendingMachine> = {
  slug: 'vending-machine',
  name: 'vendingMachine (docs/fsm/extended.md)',
  machine: vendingMachine,
  events: [...coins, { type: 'select' }, { type: 'refund' }],
  marked: (s) => s.matches('idle'),
  invariants: {
    'credit never negative': (s) => s.context.credit >= 0,
    'idle means no credit': (s) => !s.matches('idle') || s.context.credit === 0,
    'has_credit means credit > 0': (s) => !s.matches('has_credit') || s.context.credit > 0,
  },
  // credit and counters are unbounded: bounded search, 4 events deep
  maxDepth: 4,
  expect: { deadlocks: 0, blocking: 0 },
};

/** Same protocols as dining_philosophers(n, atomic=...) in src/petrilab/petri/examples.py. */
export function philosophersSpec(n: number, atomic: boolean): MachineSpec<AnyStateMachine> {
  const machine = createPhilosophers(n, atomic);
  const neighbours = Array.from({ length: n }, (_, i) => [i, (i + 1) % n] as const);
  return {
    slug: `philosophers-${n}-${atomic ? 'atomic' : 'naive'}`,
    name: `philosophers n=${n} ${atomic ? 'atomic' : 'naive'} (docs/petri/examples.md)`,
    machine,
    events: philosopherEvents(n, atomic) as never,
    marked: (s) => Object.values(s.value as Record<string, string>).every((v) => v === 'think'),
    invariants: {
      'neighbours never eat together': (s) =>
        neighbours.every(([a, b]) => !(s.hasTag(`EAT${a}`) && s.hasTag(`EAT${b}`))),
    },
    // naive: exactly one dead state, everyone holding the left fork
    expect: atomic ? { deadlocks: 0, blocking: 0 } : { deadlocks: 1, blocking: 1 },
    vectors: false,
  };
}
