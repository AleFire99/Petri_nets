import { describe, expect, it } from 'vitest';
import { explore } from '../src/analysis/explore';
import { specs } from '../src/specs';

/**
 * Exhaustive checks for every registered machine.
 * Same logic as `npm run analyze`, inside the test runner so CI shows one report.
 */
describe.each(specs.map((s) => [s.name, s] as const))('%s', (_name, spec) => {
  const r = explore(spec.machine, spec);

  it('explores the full state space', () => expect(r.truncated).toBe(false));
  it(`has ${spec.expect.deadlocks} deadlock(s)`, () =>
    expect(r.deadlocks.map((d) => d.path.events.join(' -> '))).toHaveLength(spec.expect.deadlocks));
  it('is nonblocking as specified (home always reachable)', () =>
    expect(r.blocking).toHaveLength(spec.expect.blocking));
  it('holds every invariant in every reachable state', () =>
    expect(r.invariantViolations).toEqual([]));
  it('has no unreachable state nodes', () => expect(r.unreachableStateNodes).toEqual([]));
});
