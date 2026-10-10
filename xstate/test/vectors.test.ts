import { existsSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { SimulatedClock, createActor } from 'xstate';
import { type VectorFile, leafIds } from '../src/codegen/vectors';
import { specs } from '../src/specs';

/**
 * Vectors are built with the pure `transition()` function. Replay them on the
 * REAL interpreter with a simulated clock: if both agree, vectors are a
 * trustworthy oracle for the Python implementations in src/petrilab/fsm.
 */
for (const spec of specs) {
  const path = `generated/${spec.slug}/vectors.json`;
  if (!existsSync(path)) continue;
  const file = JSON.parse(readFileSync(path, 'utf8')) as VectorFile;

  describe(`${spec.name}: vectors on live interpreter`, () => {
    it.each(file.vectors.map((v) => [v.id, v] as const))('%s', (_id, v) => {
      const clock = new SimulatedClock();
      const actor = createActor(spec.machine, { clock, input: spec.input }).start();
      for (const step of v.steps) {
        if ('wait' in step) clock.increment(step.wait);
        else actor.send(step.event as never);
        const s = actor.getSnapshot();
        expect(leafIds(spec.machine, s.value)).toEqual(step.expect.state);
        expect([...s.tags].sort()).toEqual(step.expect.outputs);
        expect(s.context).toEqual(step.expect.context);
      }
    });
  });
}
