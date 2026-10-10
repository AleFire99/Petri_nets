import type { AnyStateMachine } from 'xstate';
import { createPhilosophers, philosopherEvents } from '../machines/philosophers.machine';
import { philosophers2Atomic, philosophers2Naive } from '../machines/philosophers2.machine';
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

/** Literal n=2 machines for the visual editor; test/philosophers2.test.ts ties them to the factory. */
export const philosophers2Specs: MachineSpec<AnyStateMachine>[] = [false, true].map((atomic) => ({
  ...philosophersSpec(2, atomic),
  slug: `philosophers-2-${atomic ? 'atomic' : 'naive'}-literal`,
  name: `philosophers n=2 ${atomic ? 'atomic' : 'naive'} (literal)`,
  machine: (atomic ? philosophers2Atomic : philosophers2Naive) as unknown as AnyStateMachine,
  report: false,
}));
