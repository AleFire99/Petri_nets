import type { AnyStateMachine } from 'xstate';
import { createPhilosophers, philosopherEvents } from '../machines/philosophers.machine';
import type { MachineSpec } from './types';

/** Same protocols as dining_philosophers(n, atomic=...) in src/petrilab/petri/examples.py. */
export function philosophersSpec(n: number, atomic: boolean): MachineSpec<AnyStateMachine> {
  const neighbours = Array.from({ length: n }, (_, i) => [i, (i + 1) % n] as const);
  return {
    slug: `philosophers-${n}-${atomic ? 'atomic' : 'naive'}`,
    name: `philosophers n=${n} ${atomic ? 'atomic' : 'naive'}`,
    machine: createPhilosophers(n, atomic),
    events: philosopherEvents(n, atomic) as never,
    marked: (s) => Object.values(s.value as Record<string, string>).every((v) => v === 'think'),
    invariants: {
      'neighbours never eat together': (s) =>
        neighbours.every(([a, b]) => !(s.hasTag(`EAT${a}`) && s.hasTag(`EAT${b}`))),
    },
    // naive: exactly one dead state, everyone holding the left fork
    expect: atomic ? { deadlocks: 0, blocking: 0 } : { deadlocks: 1, blocking: 1 },
    report: true, // read by tests/petri/test_xstate_crosscheck.py
    diagram: false,
  };
}
