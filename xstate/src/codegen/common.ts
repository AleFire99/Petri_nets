import type { AnyStateMachine, AnyStateNode } from 'xstate';

export type TDef = {
  eventType: string;
  target?: AnyStateNode[];
  guard?: unknown;
  actions: readonly unknown[];
};

export function children(n: AnyStateNode): AnyStateNode[] {
  return Object.values(n.states ?? {}) as AnyStateNode[];
}

export function atomicNodes(n: AnyStateNode): AnyStateNode[] {
  const kids = children(n);
  if (!kids.length) return [n];
  return kids.flatMap(atomicNodes);
}

/** Initial leaf reached when entering `n` (non-parallel machines). */
export function initialLeaf(n: AnyStateNode): AnyStateNode {
  if (n.type === 'parallel') throw new Error(`parallel node ${n.id} not supported here`);
  const kids = children(n);
  if (!kids.length) return n;
  const init = (n.config as { initial?: string }).initial ?? Object.keys(n.states)[0]!;
  return initialLeaf(n.states[init] as AnyStateNode);
}

export function transitionsOf(n: AnyStateNode): TDef[] {
  const out: TDef[] = [];
  for (const defs of (n.transitions as unknown as Map<string, TDef[]>).values()) out.push(...defs);
  return out;
}

export function ancestry(n: AnyStateNode): AnyStateNode[] {
  const chain: AnyStateNode[] = [];
  let cur: AnyStateNode | undefined = n;
  while (cur) {
    chain.push(cur);
    cur = cur.parent;
  }
  return chain; // deepest first: XState priority order
}

export function guardName(g: unknown): string | null {
  if (!g) return null;
  if (typeof g === 'string') return g;
  if (typeof g === 'object' && g && 'type' in g) return String((g as { type: string }).type);
  return 'inlineGuard';
}

export function actionInfo(a: unknown): { name: string; params?: Record<string, unknown> } {
  if (typeof a === 'string') return { name: a };
  if (a && typeof a === 'object' && 'type' in a) {
    const o = a as { type: string; params?: Record<string, unknown> };
    return { name: o.type, params: o.params };
  }
  return { name: 'inlineAction' };
}

/** "xstate.after.FILL_TIMEOUT.fillStation.running.filling" -> "FILL_TIMEOUT" */
export function delayName(eventType: string, nodeId: string): string | null {
  const pre = 'xstate.after.';
  if (!eventType.startsWith(pre)) return null;
  return eventType.slice(pre.length, eventType.length - nodeId.length - 1);
}

export function delayMs(m: AnyStateMachine, name: string): number {
  const d = (m.implementations.delays as Record<string, unknown>)[name];
  if (typeof d === 'number') return d;
  const n = Number(name);
  if (!Number.isNaN(n)) return n;
  throw new Error(`delay ${name} is dynamic; give it a fixed value for codegen`);
}

export const ident = (id: string, rootId: string) =>
  id.slice(rootId.length + 1).replace(/[^A-Za-z0-9]/g, '_');
