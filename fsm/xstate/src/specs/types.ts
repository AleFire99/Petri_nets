import type { AnyStateMachine } from 'xstate';
import type { Ev, Snap } from '../analysis/explore';

/** Verification spec for one machine. Analyzer, tests and exporter iterate these. */
export interface MachineSpec<M extends AnyStateMachine> {
  /** File name under generated/{vectors,reports}/. Python tests read files by this name. */
  slug: string;
  /** Human-readable name for logs. */
  name: string;
  machine: M;
  input?: unknown;
  /** Events the environment can send; each payload variant listed separately. */
  events: Ev<M>[];
  /** Marked (home) states: must stay reachable from everywhere. */
  marked?: (s: Snap<M>) => boolean;
  /** Safety invariants: must hold in every reachable state. */
  invariants?: Record<string, (s: Snap<M>) => boolean>;
  /** Project context before hashing. */
  abstract?: (s: Snap<M>) => unknown;
  /** Bounded search, for machines with unbounded counters. */
  maxDepth?: number;
  /** What CI must see. A design that is MEANT to deadlock says so here. */
  expect: { deadlocks: number; blocking: number };
  /** Export test vectors for a hand-written implementation (src/petrilab/...). */
  vectors?: boolean;
  /** Export report.json (state/edge/deadlock counts) for a Python cross-check. */
  report?: boolean;
  /** Mermaid export (default true). Off for factory-built analysis machines. */
  diagram?: boolean;
  codegen?: { st?: boolean };
}
