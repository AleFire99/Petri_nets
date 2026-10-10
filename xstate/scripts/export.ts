/**
 * npm run export
 * Writes generated/<slug>/:
 *   diagram.md     Mermaid diagram (renders in PRs)
 *   report.json    state/edge/deadlock counts (Python cross-checks read this)
 *   vectors.json   transition-coverage test vectors (Python tests replay this)
 *   FB_<id>.st     IEC 61131-3 skeleton (when spec.codegen.st)
 * CI regenerates and fails if the committed files differ.
 */
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { explore } from '../src/analysis/explore';
import { toMermaid } from '../src/codegen/mermaid';
import { toStructuredText } from '../src/codegen/st';
import { toVectors } from '../src/codegen/vectors';
import { specs } from '../src/specs';

const json = (v: unknown) => `${JSON.stringify(v, null, 1)}\n`;

rmSync('generated', { recursive: true, force: true });
for (const spec of specs) {
  const dir = join('generated', spec.slug);
  mkdirSync(dir, { recursive: true });
  const r = explore(spec.machine, spec);

  writeFileSync(join(dir, 'diagram.md'), `# ${spec.name}\n\n\`\`\`mermaid\n${toMermaid(spec.machine)}\`\`\`\n`);
  writeFileSync(
    join(dir, 'report.json'),
    json({
      machine: r.machine,
      bounded: r.bounded,
      stateCount: r.stateCount,
      edgeCount: r.edgeCount,
      deadlocks: r.deadlocks.map((d) => ({ state: d.state, trace: d.path.events })),
      blocking: r.blocking.length,
      invariants: Object.keys(spec.invariants ?? {}),
      invariantViolations: r.invariantViolations.length,
    }),
  );
  if (spec.vectors ?? spec.expect.deadlocks === 0) {
    writeFileSync(join(dir, 'vectors.json'), json(toVectors(spec.machine, r, spec.input)));
  }
  if (spec.codegen?.st) {
    writeFileSync(join(dir, `FB_${spec.machine.id}.st`), toStructuredText(spec.machine));
  }
  console.log(`exported ${dir}`);
}
