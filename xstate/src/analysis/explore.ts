import {
  type AnyEventObject,
  type AnyStateMachine,
  type ContextFrom,
  type EventFromLogic,
  type MachineSnapshot,
  getNextTransitions,
  getStateNodes,
  initialTransition,
  transition,
} from 'xstate';

/**
 * Exhaustive state-space explorer for XState v5 machines.
 *
 * Breadth-first search over (state value + context). In every reached
 * snapshot it tries every event listed in the spec (payload variants are
 * separate events) and every armed timer (`after` -> `xstate.after.*` event).
 *
 * Checks, same vocabulary as src/petrilab/petri/analysis.py:
 *   - deadlocks:   non-final states where no event changes anything (dead markings)
 *   - blocking:    states from which no marked (home) state is reachable
 *   - invariants:  predicates that must hold in every reachable state
 *   - unreachable: declared state nodes never entered
 *
 * Works because XState v5 `transition()` is pure: snapshot in, snapshot out,
 * no timers, no side effects.
 *
 * `maxDepth` bounds the search for machines with unbounded context (counters).
 * Bounded results are exact for invariants on the explored part only; states on
 * the frontier are not reported as deadlocked or blocking.
 */

export type Snap<M extends AnyStateMachine> = MachineSnapshot<
  ContextFrom<M>,
  EventFromLogic<M>,
  // remaining XState generic slots are irrelevant for analysis
  any, any, any, any, any, any
>;
export type Ev<M extends AnyStateMachine> = EventFromLogic<M>;

export interface ExploreOptions<M extends AnyStateMachine> {
  input?: unknown;
  /** Events the environment can send. Each payload variant listed explicitly. */
  events: Ev<M>[];
  /** Include armed `after` delays as events. Default true. */
  timers?: boolean;
  /** Marked (home) states. Must stay reachable from every reachable state. */
  marked?: (s: Snap<M>) => boolean;
  /** Safety invariants: name -> predicate that must hold everywhere. */
  invariants?: Record<string, (s: Snap<M>) => boolean>;
  /** Project context before hashing (drop fields that do not affect behaviour). */
  abstract?: (s: Snap<M>) => unknown;
  /** Bounded search depth (events from the initial state). Default: unbounded. */
  maxDepth?: number;
  /** Hard stop on state count. Default 50 000. */
  maxStates?: number;
}

export interface Edge {
  from: string;
  to: string;
  event: AnyEventObject;
  label: string;
}

export interface Path {
  /** Human-readable trace, e.g. ["insert(amount=25)", "select"]. */
  events: string[];
  /** The exact event objects, for replay. */
  steps: AnyEventObject[];
}

export interface ExploreReport {
  machine: string;
  stateCount: number;
  edgeCount: number;
  bounded: boolean;
  frontier: number;
  truncated: boolean;
  deadlocks: { state: string; path: Path }[];
  blocking: { state: string; path: Path }[];
  invariantViolations: { invariant: string; state: string; path: Path }[];
  unreachableStateNodes: string[];
}

export interface ExploreResult<M extends AnyStateMachine> extends ExploreReport {
  graph: {
    initial: string;
    snapshots: Map<string, Snap<M>>;
    edges: Edge[];
    pathTo: (key: string) => Path;
  };
}

export function stable(v: unknown): string {
  if (v === null || typeof v !== 'object') return JSON.stringify(v) ?? 'null';
  if (Array.isArray(v)) return `[${v.map(stable).join(',')}]`;
  const o = v as Record<string, unknown>;
  return `{${Object.keys(o)
    .sort()
    .map((k) => `${JSON.stringify(k)}:${stable(o[k])}`)
    .join(',')}}`;
}

export function describe(s: { value: unknown; context: unknown }): string {
  return `${stable(s.value)} ${stable(s.context)}`;
}

export function eventLabel(e: AnyEventObject): string {
  const { type, ...payload } = e;
  const args = Object.entries(payload).map(([k, v]) => `${k}=${stable(v)}`);
  return args.length ? `${type}(${args.join(', ')})` : type;
}

function timerEvents(s: unknown): AnyEventObject[] {
  const types = new Set<string>();
  for (const t of getNextTransitions(s as never)) {
    if (t.eventType.startsWith('xstate.after.')) types.add(t.eventType);
  }
  return [...types].map((type) => ({ type }));
}

export function explore<M extends AnyStateMachine>(
  machine: M,
  opts: ExploreOptions<M>,
): ExploreResult<M> {
  const key = (s: Snap<M>) =>
    `${stable(s.value)}|${stable(opts.abstract ? opts.abstract(s) : s.context)}|${s.status}`;
  const maxStates = opts.maxStates ?? 50_000;
  const maxDepth = opts.maxDepth ?? Number.POSITIVE_INFINITY;

  const [init] = initialTransition(machine, opts.input as never) as unknown as [Snap<M>];
  const initKey = key(init);
  const snaps = new Map<string, Snap<M>>([[initKey, init]]);
  const depth = new Map<string, number>([[initKey, 0]]);
  const parent = new Map<string, { from: string; event: AnyEventObject } | null>([[initKey, null]]);
  const edges: Edge[] = [];
  const out = new Map<string, Set<string>>();
  const frontier = new Set<string>();
  const queue: string[] = [initKey];
  let truncated = false;

  while (queue.length) {
    const k = queue.shift()!;
    const s = snaps.get(k)!;
    out.set(k, new Set());
    if (s.status !== 'active') continue; // final: no outgoing by design
    if (depth.get(k)! >= maxDepth) {
      frontier.add(k);
      continue;
    }
    const candidates: AnyEventObject[] = [
      ...(opts.events as AnyEventObject[]),
      ...(opts.timers === false ? [] : timerEvents(s)),
    ];
    for (const ev of candidates) {
      const [next] = transition(machine, s as never, ev as never) as unknown as [Snap<M>];
      const nk = key(next);
      if (nk === k) continue; // ignored event, failed guard, or pure self-loop
      edges.push({ from: k, to: nk, event: ev, label: eventLabel(ev) });
      out.get(k)!.add(nk);
      if (!snaps.has(nk)) {
        if (snaps.size >= maxStates) {
          truncated = true;
          continue;
        }
        snaps.set(nk, next);
        depth.set(nk, depth.get(k)! + 1);
        parent.set(nk, { from: k, event: ev });
        queue.push(nk);
      }
    }
  }

  const pathTo = (k: string): Path => {
    const steps: AnyEventObject[] = [];
    let cur = parent.get(k);
    while (cur) {
      steps.unshift(cur.event);
      cur = parent.get(cur.from);
    }
    return { steps, events: steps.map(eventLabel) };
  };

  const isFinal = (s: Snap<M>) => s.status !== 'active';

  const deadlocks = [...snaps.entries()]
    .filter(([k, s]) => !isFinal(s) && !frontier.has(k) && out.get(k)!.size === 0)
    .map(([k, s]) => ({ state: describe(s), path: pathTo(k) }));

  let blocking: ExploreReport['blocking'] = [];
  if (opts.marked) {
    const rev = new Map<string, string[]>();
    for (const e of edges) {
      if (!rev.has(e.to)) rev.set(e.to, []);
      rev.get(e.to)!.push(e.from);
    }
    // Frontier states are unknown: treated optimistically as able to get home.
    const seeds = [...snaps.entries()]
      .filter(([k, s]) => opts.marked!(s) || frontier.has(k))
      .map(([k]) => k);
    const coreach = new Set<string>(seeds);
    const stack = [...seeds];
    while (stack.length) {
      const k = stack.pop()!;
      for (const p of rev.get(k) ?? []) {
        if (!coreach.has(p)) {
          coreach.add(p);
          stack.push(p);
        }
      }
    }
    blocking = [...snaps.entries()]
      .filter(([k]) => !coreach.has(k))
      .map(([k, s]) => ({ state: describe(s), path: pathTo(k) }));
  }

  const invariantViolations: ExploreReport['invariantViolations'] = [];
  for (const [name, pred] of Object.entries(opts.invariants ?? {})) {
    for (const [k, s] of snaps) {
      if (!pred(s)) invariantViolations.push({ invariant: name, state: describe(s), path: pathTo(k) });
    }
  }

  const visited = new Set<string>();
  for (const s of snaps.values()) {
    for (const n of getStateNodes(machine.root, s.value)) visited.add(n.id);
  }
  const allIds = [...(machine as unknown as { idMap: Map<string, unknown> }).idMap.keys()];
  const unreachableStateNodes = allIds.filter((id) => id !== machine.root.id && !visited.has(id));

  return {
    machine: machine.id,
    stateCount: snaps.size,
    edgeCount: edges.length,
    bounded: Number.isFinite(maxDepth),
    frontier: frontier.size,
    truncated,
    deadlocks,
    blocking,
    invariantViolations,
    unreachableStateNodes,
    graph: { initial: initKey, snapshots: snaps, edges, pathTo },
  };
}

/** JSON-friendly report without the raw graph. */
export function toReport(r: ExploreResult<AnyStateMachine>): ExploreReport {
  const { graph: _graph, ...rest } = r;
  return rest;
}
