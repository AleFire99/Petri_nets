import { type AnyStateMachine, assign, setup } from 'xstate';

/**
 * Dining philosophers as concurrent EFSMs: one parallel region per philosopher,
 * forks as shared context variables. Same protocol as
 * `dining_philosophers()` in src/petrilab/petri/examples.py:
 *   naive:  takeLeft{i}, takeRight{i}, done{i}   (can deadlock)
 *   atomic: take{i}, done{i}                     (deadlock-free)
 * Automation reading: philosophers = robots, forks = shared tools / zones.
 *
 * Built by a factory to vary n. That breaks the "literal config" rule on
 * purpose: this machine exists for analysis, not for the visual editor.
 */
export type PhilEvent = { type: string };
type Ctx = { forks: boolean[] }; // true = fork on the table (Petri place Fork_i has a token)

export function createPhilosophers(n: number, atomic: boolean): AnyStateMachine {
  if (n < 2) throw new Error('need at least two philosophers');
  const left = (i: number) => i;
  const right = (i: number) => (i + 1) % n;

  type P = { forks: number[] };

  const region = (i: number) => {
    const take = (forks: number[], target: string) => ({
      guard: { type: 'forksFree', params: { forks } },
      actions: { type: 'takeForks', params: { forks } },
      target,
    });
    const release = { actions: { type: 'putForks', params: { forks: [left(i), right(i)] } }, target: 'think' };
    return {
      initial: 'think',
      states: atomic
        ? {
            think: { on: { [`take${i}`]: take([left(i), right(i)], 'eat') } },
            eat: { tags: [`EAT${i}`], on: { [`done${i}`]: release } },
          }
        : {
            think: { on: { [`takeLeft${i}`]: take([left(i)], 'hasLeft') } },
            hasLeft: { on: { [`takeRight${i}`]: take([right(i)], 'eat') } },
            eat: { tags: [`EAT${i}`], on: { [`done${i}`]: release } },
          },
    };
  };

  const set = (ctx: Ctx, forks: number[], value: boolean) =>
    ctx.forks.map((v, f) => (forks.includes(f) ? value : v));

  const machine = setup({
    types: { context: {} as Ctx, events: {} as PhilEvent },
    guards: {
      forksFree: ({ context }, p: P) => p.forks.every((f) => context.forks[f]),
    },
    actions: {
      takeForks: assign({ forks: ({ context }, p: P) => set(context, p.forks, false) }),
      putForks: assign({ forks: ({ context }, p: P) => set(context, p.forks, true) }),
    },
  }).createMachine({
    /** @xstate-layout N4IgpgJg5mDOIC5gF8A0IB2B7CdGgAoBbAQwGMALASwzAEp8QAHLWKgFyqw0YA9EAjACZ0AT0FDkU5EA */
    id: `philosophers${n}${atomic ? 'Atomic' : 'Naive'}`,
    type: 'parallel',
    context: { forks: Array.from({ length: n }, () => true) },
    states: Object.fromEntries(Array.from({ length: n }, (_, i) => [`phil${i}`, region(i)])),
  } as never as never);
  return machine as unknown as AnyStateMachine;
}

export function philosopherEvents(n: number, atomic: boolean): PhilEvent[] {
  const names = atomic ? ['take', 'done'] : ['takeLeft', 'takeRight', 'done'];
  return Array.from({ length: n }, (_, i) => names.map((x) => ({ type: `${x}${i}` }))).flat();
}
