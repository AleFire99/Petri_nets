import type { AnyStateMachine, AnyStateNode } from 'xstate';
import { children, delayName, guardName, transitionsOf } from './common';

/**
 * Machine -> Mermaid stateDiagram-v2.
 * Committed next to the code: GitHub/GitLab render it in PR diffs,
 * so reviewers see the diagram change, not just the TS change.
 */
export function toMermaid(m: AnyStateMachine): string {
  const id = (n: AnyStateNode) => n.id.replace(/[^A-Za-z0-9]/g, '_');
  const lines: string[] = ['stateDiagram-v2'];
  const edges: string[] = [];

  const label = (n: AnyStateNode, t: ReturnType<typeof transitionsOf>[number]) => {
    const d = delayName(t.eventType, n.id);
    let s = d ? `after ${d}` : t.eventType;
    const g = guardName(t.guard);
    if (g) s += ` [${g}]`;
    return s;
  };

  // Inside parallel regions, edges must stay inside their composite block,
  // otherwise Mermaid rejects or mis-places them. Elsewhere edges go last.
  const walk = (n: AnyStateNode, indent: string, inParallel = false) => {
    const kids = children(n);
    for (const [i, k] of kids.entries()) {
      const tags = [...(k.tags ?? [])];
      const name = tags.length ? `${k.key} / ${tags.join(',')}` : k.key;
      if (n.type === 'parallel' && i > 0) lines.push(`${indent}--`);
      if (children(k).length) {
        lines.push(`${indent}state "${k.key}" as ${id(k)} {`);
        walk(k, indent + '  ', inParallel || n.type === 'parallel');
        lines.push(`${indent}}`);
      } else {
        lines.push(`${indent}state "${name}" as ${id(k)}`);
      }
    }
    if (kids.length && n.type !== 'parallel') {
      const init = (n.config as { initial?: string }).initial;
      if (init) lines.push(`${indent}[*] --> ${id(n.states[init] as AnyStateNode)}`);
    }
    for (const k of kids) {
      for (const t of transitionsOf(k)) {
        for (const tgt of t.target ?? []) {
          const edge = `${id(k)} --> ${id(tgt)} : ${label(k, t)}`;
          if (inParallel) lines.push(`${indent}${edge}`);
          else edges.push(`  ${edge}`);
        }
      }
    }
  };

  if (m.root.type === 'parallel') {
    // Mermaid allows `--` region separators only inside a composite state.
    lines.push(`  state "${m.root.id}" as ${id(m.root)} {`);
    walk(m.root, '    ', true);
    lines.push('  }', `  [*] --> ${id(m.root)}`);
  } else {
    walk(m.root, '  ');
  }
  const rootT = transitionsOf(m.root);
  if (rootT.length) {
    lines.push('  state "any state" as ANY');
    for (const t of rootT) for (const tgt of t.target ?? []) edges.push(`  ANY --> ${id(tgt)} : ${t.eventType}`);
  }
  return [...lines, ...edges].join('\n') + '\n';
}
