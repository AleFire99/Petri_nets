import { describe, expect, it } from 'vitest';
import { explore } from '../src/analysis/explore';
import { createPhilosophers, philosopherEvents } from '../src/machines/philosophers.machine';
import { philosophers2Atomic, philosophers2Naive } from '../src/machines/philosophers2.machine';

/** The literal (editor-friendly) n=2 machines must match the n-ary factory exactly. */
describe.each([
  ['atomic', true, philosophers2Atomic],
  ['naive', false, philosophers2Naive],
] as const)('philosophers2 %s equals createPhilosophers(2)', (_name, atomic, literal) => {
  const opts = (machine: unknown) => ({ events: philosopherEvents(2, atomic) as never, machine: machine as never });
  const a = explore(literal as never, opts(literal) as never);
  const b = explore(createPhilosophers(2, atomic), opts(createPhilosophers(2, atomic)) as never);

  it('has the same state and edge counts', () => {
    expect(a.stateCount).toBe(b.stateCount);
    expect(a.edgeCount).toBe(b.edgeCount);
  });
  it('has the same deadlocks', () => {
    expect(a.deadlocks.map((d) => d.state)).toEqual(b.deadlocks.map((d) => d.state));
  });
});
