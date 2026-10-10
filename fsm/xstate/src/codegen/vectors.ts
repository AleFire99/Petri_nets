import {
  type AnyEventObject,
  type AnyStateMachine,
  type AnyStateNode,
  getStateNodes,
  initialTransition,
  transition,
} from 'xstate';
import type { ExploreResult } from '../analysis/explore';
import { delayMs } from './common';

/**
 * Language-neutral test vectors: one vector per explored transition
 * (transition coverage). Each step = stimulus in, expected state + outputs + context out.
 *
 * Any implementation (Python in src/petrilab/fsm, ST, C++) replays these and must match.
 *   { "event": { "type": "insert", "amount": 25 }, "expect": ... }
 *   { "wait": 30000, "delay": "TIMEOUT", "expect": ... }      (milliseconds)
 */
export type Expect = { state: string[]; outputs: string[]; context: unknown };
export type VectorStep =
  | { event: AnyEventObject; expect: Expect }
  | { wait: number; delay: string; expect: Expect };
export interface Vector {
  id: string;
  steps: VectorStep[];
}
export interface VectorFile {
  machine: string;
  initial: Expect;
  vectors: Vector[];
}

export function leafIds(m: AnyStateMachine, value: unknown): string[] {
  return getStateNodes(m.root, value as never)
    .filter((n: AnyStateNode) => n.type === 'atomic' || n.type === 'final')
    .map((n: AnyStateNode) => n.id.slice(m.root.id.length + 1))
    .sort();
}

export function toVectors(
  m: AnyStateMachine,
  r: ExploreResult<AnyStateMachine>,
  input?: unknown,
): VectorFile {
  const expect = (s: any): Expect => ({
    state: leafIds(m, s.value),
    outputs: [...s.tags].sort(),
    context: s.context,
  });

  const [init] = initialTransition(m, input as never);
  const vectors: Vector[] = [];
  const seen = new Set<string>();

  for (const e of r.graph.edges) {
    const steps = [...r.graph.pathTo(e.from).steps, e.event];
    const sig = JSON.stringify(steps);
    if (seen.has(sig)) continue;
    seen.add(sig);
    let s: any = init;
    const out: VectorStep[] = [];
    for (const ev of steps) {
      [s] = transition(m, s, ev as never);
      const delay = /^xstate\.after\.([^.]+)\./.exec(ev.type)?.[1];
      out.push(
        delay
          ? { wait: delayMs(m, delay), delay, expect: expect(s) }
          : { event: ev, expect: expect(s) },
      );
    }
    vectors.push({ id: `T${vectors.length + 1}`, steps: out });
  }

  return { machine: m.id, initial: expect(init), vectors };
}
