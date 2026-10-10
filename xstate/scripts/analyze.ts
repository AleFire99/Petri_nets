/**
 * npm run analyze
 * Explores every registered machine. Exit code 1 if anything differs from spec.expect,
 * an invariant breaks, a state node is unreachable, or the search was truncated.
 * Prints the shortest event sequence reaching each problem (counterexample).
 */
import { explore, toReport } from '../src/analysis/explore';
import { specs } from '../src/specs';

let failed = false;
const json = process.argv.includes('--json');
const reports = [];

for (const spec of specs) {
  const r = explore(spec.machine, spec);
  reports.push({ spec: spec.name, ...toReport(r) });
  const problems: string[] = [];
  if (r.truncated) problems.push('state space truncated: add `abstract` or bound counters');
  if (r.deadlocks.length !== spec.expect.deadlocks)
    problems.push(`deadlocks: expected ${spec.expect.deadlocks}, found ${r.deadlocks.length}`);
  if (r.blocking.length !== spec.expect.blocking)
    problems.push(`blocking states: expected ${spec.expect.blocking}, found ${r.blocking.length}`);
  for (const v of r.invariantViolations) problems.push(`invariant "${v.invariant}" broken`);
  for (const id of r.unreachableStateNodes) problems.push(`unreachable state node: ${id}`);

  if (json) {
    if (problems.length) failed = true;
    continue;
  }
  const ok = problems.length === 0;
  console.log(`\n${ok ? 'PASS' : 'FAIL'}  ${spec.name}`);
  console.log(
    `      ${r.stateCount} states, ${r.edgeCount} transitions explored` +
      (r.bounded ? ` (bounded: ${r.frontier} frontier states not expanded)` : ''),
  );
  for (const d of r.deadlocks) {
    console.log(`      deadlock${spec.expect.deadlocks ? ' (expected)' : ''}: ${d.state}`);
    console.log(`        reached by: ${d.path.events.join(' -> ')}`);
  }
  for (const v of r.invariantViolations.slice(0, 5)) {
    console.log(`      violation "${v.invariant}": ${v.state}`);
    console.log(`        reached by: ${v.path.events.join(' -> ')}`);
  }
  for (const p of problems) console.log(`      ✗ ${p}`);
  if (!ok) failed = true;
}

if (json) console.log(JSON.stringify(reports, null, 2));
process.exit(failed ? 1 : 0);
