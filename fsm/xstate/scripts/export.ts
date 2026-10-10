/**
 * npm run export
 * Writes generated/:
 *   diagrams/<machine>.md   Mermaid diagram per machine (renders in PRs)
 *   reports/<slug>.json     state/edge/deadlock counts (spec.report; Petri cross-check reads it)
 *   vectors/<slug>.json     transition-coverage test vectors (spec.vectors; Python replays them)
 *   st/FB_<machine>.st      IEC 61131-3 skeleton (spec.codegen.st)
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
for (const dir of ['diagrams', 'vectors', 'st', 'reports']) mkdirSync(join('generated', dir), { recursive: true });

const diagrams = new Set<string>();
for (const spec of specs) {
  const r = explore(spec.machine, spec);
  const id = spec.machine.id;

  // one diagram per machine (specs may share a machine with different inputs)
  if (spec.diagram !== false && !diagrams.has(id)) {
    diagrams.add(id);
    writeFileSync(join('generated/diagrams', `${id}.md`), `# ${id}\n\n\`\`\`mermaid\n${toMermaid(spec.machine)}\`\`\`\n`);
  }
  if (spec.report) {
    writeFileSync(
      join('generated/reports', `${spec.slug}.json`),
      json({
        machine: r.machine,
        bounded: r.bounded,
        stateCount: r.stateCount,
        edgeCount: r.edgeCount,
        deadlocks: r.deadlocks.map((d) => ({ state: d.state, trace: d.path.events })),
        blocking: r.blocking.length,
      }),
    );
  }
  if (spec.vectors) writeFileSync(join('generated/vectors', `${spec.slug}.json`), json(toVectors(spec.machine, r, spec.input)));
  if (spec.codegen?.st) writeFileSync(join('generated/st', `FB_${id}.st`), toStructuredText(spec.machine));
}
console.log(`exported ${specs.length} specs, ${diagrams.size} diagrams`);
