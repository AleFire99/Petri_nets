/**
 * npm run sim -- <spec name fragment> [--inspect]
 *
 * Terminal simulator. Type an event name, `wait <ms>`, `events`, or `quit`.
 * Uses SimulatedClock, so `wait` jumps time instantly.
 * --inspect streams to Stately Inspector (opens a link in your browser, needs internet).
 *
 * Also scriptable for agents:  echo "START\nwait 30000\nRESET" | npm run sim -- fill
 */
import { createInterface } from 'node:readline';
import { SimulatedClock, createActor } from 'xstate';
import { specs } from '../src/specs';

const args = process.argv.slice(2);
const pick = args.find((a) => !a.startsWith('--')) ?? '';
const spec = specs.find((s) => s.name.toLowerCase().includes(pick.toLowerCase()));
if (!spec) {
  console.error(`no spec matches "${pick}". Options: ${specs.map((s) => s.name).join(', ')}`);
  process.exit(1);
}

let inspect: unknown;
if (args.includes('--inspect')) {
  const { createSkyInspector } = await import('@statelyai/inspect');
  inspect = createSkyInspector().inspect;
}

const clock = new SimulatedClock();
const actor = createActor(spec.machine, { clock, input: spec.input, inspect: inspect as never });
let t = 0;
const show = () => {
  const s = actor.getSnapshot();
  console.log(`t=${t}ms  state=${JSON.stringify(s.value)}  outputs=[${[...s.tags].join(',')}]  ctx=${JSON.stringify(s.context)}`);
};
actor.start();
show();

const rl = createInterface({ input: process.stdin, terminal: process.stdin.isTTY });
const names = spec.events.map((e) => e.type);
for await (const raw of rl) {
  const line = raw.trim();
  if (!line) continue;
  if (line === 'quit') break;
  if (line === 'events') { console.log(names.join(' ')); continue; }
  const w = /^wait\s+(\d+)$/.exec(line);
  if (w) { t += Number(w[1]); clock.increment(Number(w[1])); }
  else if (names.includes(line)) actor.send({ type: line } as never);
  else { console.log(`? unknown. events: ${names.join(' ')}`); continue; }
  process.stdout.write(`> ${line}\n`);
  show();
}
actor.stop();
process.exit(0);
