import type { AnyStateMachine, AnyStateNode } from 'xstate';
import {
  actionInfo,
  ancestry,
  atomicNodes,
  delayMs,
  delayName,
  guardName,
  ident,
  initialLeaf,
  transitionsOf,
} from './common';

/**
 * Machine -> IEC 61131-3 Structured Text skeleton (CODESYS / TwinCAT style).
 *
 * Mapping:
 *   atomic states      -> ENUM values, one CASE branch each
 *   hierarchy          -> flattened; ancestor transitions copied into every
 *                         descendant branch AFTER the leaf's own (same priority as XState)
 *   events             -> BOOL inputs, one-scan pulses (caller sets, FB consumes)
 *   after (timed)      -> one state timer; `tState.ET >= T#...` conditions
 *   guards / actions   -> METHOD stubs; original TS source pasted as comment
 *   tags               -> BOOL outputs (Moore outputs)
 *
 * Only for non-parallel machines. Parallel = one FB per region + explicit
 * shared-variable arbitration (write that by hand, analyzer already proved it).
 */
export function toStructuredText(m: AnyStateMachine): string {
  const root = m.root;
  if (root.type === 'parallel') throw new Error('ST codegen: parallel root not supported');
  const fb = `FB_${cap(root.id)}`;
  const en = `E_${cap(root.id)}_State`;
  const leaves = atomicNodes(root);
  const name = (n: AnyStateNode) => ident(n.id, root.id);
  const eventTypes = new Set<string>();
  const guards = new Set<string>();
  const actions = new Map<string, Set<string>>();
  const tags = new Set<string>();

  const branches: string[] = [];
  for (const leaf of leaves) {
    leaf.tags?.forEach((t: string) => tags.add(t));
    const conds: string[] = [];
    for (const owner of ancestry(leaf)) {
      for (const t of transitionsOf(owner)) {
        const d = delayName(t.eventType, owner.id);
        let cond: string;
        if (d) cond = `tState.ET >= T#${delayMs(m, d)}MS (* after ${d} *)`;
        else {
          eventTypes.add(t.eventType);
          cond = `ev${t.eventType}`;
        }
        const g = guardName(t.guard);
        if (g) {
          guards.add(g);
          cond += ` AND G_${g}()`;
        }
        const body: string[] = [];
        for (const a of t.actions) {
          const info = actionInfo(a);
          if (!actions.has(info.name)) actions.set(info.name, new Set());
          const args = Object.entries(info.params ?? {})
            .map(([k, v]) => {
              actions.get(info.name)!.add(k);
              return `${k} := ${typeof v === 'string' ? `'${v}'` : String(v)}`;
            })
            .join(', ');
          body.push(`A_${info.name}(${args});`);
        }
        const tgt = t.target?.[0];
        if (tgt) body.push(`NextState := ${en}.${name(initialLeaf(tgt))};`);
        const from = owner === leaf ? '' : ` (* inherited from ${owner.id} *)`;
        conds.push(`${conds.length ? 'ELSIF' : 'IF'} ${cond} THEN${from}\n            ${body.join('\n            ') || '; (* no-op *)'}`);
      }
    }
    branches.push(
      `    ${en}.${name(leaf)}:\n` +
        (conds.length ? `        ${conds.join('\n        ')}\n        END_IF;` : '        ; (* final / no transitions *)'),
    );
  }

  const ctx = (initialContext(m) ?? {}) as Record<string, unknown>;
  const ctxVars = Object.entries(ctx).map(([k, v]) => `    ${k} : ${stType(v)} := ${stInit(v)};`);
  const impl = m.implementations as { guards: Record<string, unknown>; actions: Record<string, unknown> };

  const methods = [
    ...[...guards].map(
      (g) =>
        `METHOD G_${g} : BOOL\n(* TS source:\n${src(impl.guards[g])}\n*)\nG_${g} := FALSE; (* TODO *)\nEND_METHOD`,
    ),
    ...[...actions.entries()].map(
      ([a, params]) =>
        `METHOD A_${a}\n${params.size ? `VAR_INPUT\n${[...params].map((p) => `    ${p} : STRING;`).join('\n')}\nEND_VAR\n` : ''}(* TS source:\n${src(impl.actions[a])}\n*)\n; (* TODO *)\nEND_METHOD`,
    ),
  ];

  return `(* GENERATED from ${root.id}.machine.ts - do not edit by hand. Regenerate: npm run export *)

TYPE ${en} :
(
${leaves.map((l, i) => `    ${name(l)} := ${i}`).join(',\n')}
);
END_TYPE

FUNCTION_BLOCK ${fb}
VAR_INPUT
${[...eventTypes].map((e) => `    ev${e} : BOOL; (* one-scan pulse *)`).join('\n')}
END_VAR
VAR_OUTPUT
    State : ${en} := ${en}.${name(initialLeaf(root))};
${[...tags].map((t) => `    ${t} : BOOL;`).join('\n')}
END_VAR
VAR
${ctxVars.join('\n')}
    NextState : ${en};
    tState : TON;
END_VAR

(* state timer: ET = time spent in current state *)
tState(IN := TRUE, PT := T#24D);
NextState := State;

CASE State OF
${branches.join('\n')}
END_CASE;

IF NextState <> State THEN
    State := NextState;
    tState(IN := FALSE); (* restart timer on state change *)
END_IF;

(* consume event pulses *)
${[...eventTypes].map((e) => `ev${e} := FALSE;`).join('\n')}

(* Moore outputs from tags *)
${[...tags].map((t) => `${t} := ${leaves.filter((l) => l.tags?.includes(t)).map((l) => `(State = ${en}.${name(l)})`).join(' OR ') || 'FALSE'};`).join('\n')}

END_FUNCTION_BLOCK

${methods.join('\n\n')}
`;
}

function cap(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
function initialContext(m: AnyStateMachine): unknown {
  const c = m.config.context;
  return typeof c === 'function' ? undefined : c;
}
function stType(v: unknown) {
  if (typeof v === 'number') return Number.isInteger(v) ? 'DINT' : 'LREAL';
  if (typeof v === 'boolean') return 'BOOL';
  return 'STRING(32)';
}
function stInit(v: unknown) {
  if (v === null || v === undefined) return "''";
  if (typeof v === 'string') return `'${v}'`;
  return String(v).toUpperCase();
}
function src(f: unknown): string {
  const a = f as { type?: string; assignment?: unknown };
  if (a && a.type === 'xstate.assign') {
    const asg = a.assignment;
    if (typeof asg === 'function') return `assign(${src(asg)})`;
    return Object.entries(asg as Record<string, unknown>)
      .map(([k, v]) => `${k} := ${typeof v === 'function' ? src(v) : JSON.stringify(v)}`)
      .join('\n');
  }
  if (typeof f === 'function') return f.toString().replace(/\*\)/g, '* )');
  return JSON.stringify(f);
}
