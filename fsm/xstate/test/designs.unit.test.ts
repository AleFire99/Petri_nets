import { describe, expect, it } from 'vitest';
import { type AnyStateMachine, SimulatedClock, createActor, createMachine } from 'xstate';
import { explore } from '../src/analysis/explore';
import { DOOR_TIMEOUT_MS, doorAlarm } from '../src/machines/doorAlarm.machine';
import { elevenDetector } from '../src/machines/elevenDetector.machine';
import { mediaPlayer } from '../src/machines/mediaPlayer.machine';
import { trafficLight, turnstile } from '../src/machines/regular.machine';
import { textStyle } from '../src/machines/textStyle.machine';
import { vendingMachine } from '../src/machines/vendingMachine.machine';
import { type HistoryKind, washer } from '../src/machines/washer.machine';
import { elevenDetectorSpec } from '../src/specs/designs.checks';

/** Scenario tests, one block per design in fsm/docs/. Exhaustive checks live in analysis.test.ts. */

const run = (m: AnyStateMachine, events: string[], input?: unknown) => {
  const a = createActor(m, { input }).start();
  for (const type of events) a.send({ type } as never);
  return a.getSnapshot();
};

describe('regular (fsm/docs/regular.md)', () => {
  it('traffic light cycles red -> green -> yellow -> red', () => {
    const a = createActor(trafficLight).start();
    const seen: unknown[] = [];
    for (let i = 0; i < 4; i++) {
      seen.push(a.getSnapshot().value);
      a.send({ type: 'next' });
    }
    expect(seen).toEqual(['red', 'green', 'yellow', 'red']);
  });

  it.each([
    [['push'], 'push', 'locked'],
    [[], 'coin', 'unlocked'],
    [[], 'push', 'locked'],
    [['coin'], 'coin', 'unlocked'],
    [['coin'], 'push', 'locked'],
  ])('turnstile %j then %s -> %s', (start, event, end) => {
    expect(run(turnstile, [...start, event]).value).toBe(end);
  });

  it('unknown event is ignored, not an error', () => {
    expect(run(turnstile, ['kick']).value).toBe('locked');
  });
});

describe('hierarchical (fsm/docs/hierarchical.md)', () => {
  it('power_on enters stopped', () => {
    expect(run(mediaPlayer, ['power_on']).value).toEqual({ on: 'stopped' });
  });

  it.each([[[]], [['play']], [['play', 'pause']]])('power_off from any child after %j', (path) => {
    expect(run(mediaPlayer, ['power_on', ...path, 'power_off']).value).toBe('off');
  });

  it('play while off does nothing', () => {
    expect(run(mediaPlayer, ['play']).value).toBe('off');
  });

  it('re-entering on starts at stopped', () => {
    expect(run(mediaPlayer, ['power_on', 'play', 'power_off', 'power_on']).value).toEqual({ on: 'stopped' });
  });
});

describe('extended (fsm/docs/extended.md)', () => {
  const send = (...events: object[]) => {
    const a = createActor(vendingMachine).start();
    for (const e of events) a.send(e as never);
    return a.getSnapshot();
  };

  it('underfunded select is rejected', () => {
    const s = send({ type: 'insert', amount: 50 }, { type: 'select' });
    expect([s.value, s.context]).toEqual(['has_credit', { credit: 50, dispensed: 0, rejected: 1 }]);
  });

  it('exact payment returns to idle', () => {
    const s = send({ type: 'insert', amount: 75 }, { type: 'select' });
    expect([s.value, s.context.credit, s.context.dispensed]).toEqual(['idle', 0, 1]);
  });

  it('change is retained after purchase', () => {
    const s = send({ type: 'insert', amount: 100 }, { type: 'select' });
    expect([s.value, s.context.credit]).toEqual(['has_credit', 25]);
  });

  it('credit accumulates, refund zeroes', () => {
    const s = send({ type: 'insert', amount: 25 }, { type: 'insert', amount: 25 }, { type: 'refund' });
    expect([s.value, s.context.credit]).toEqual(['idle', 0]);
  });

  it('non-positive insert is blocked by the guard', () => {
    expect(send({ type: 'insert', amount: 0 }).value).toBe('idle');
  });
});

describe('timed (fsm/docs/timed.md)', () => {
  const start = () => {
    const clock = new SimulatedClock();
    return { clock, a: createActor(doorAlarm, { clock }).start() };
  };

  it('no alarm at timeout - 1 ms, alarm at timeout', () => {
    const { clock, a } = start();
    a.send({ type: 'open' });
    clock.increment(DOOR_TIMEOUT_MS - 1);
    expect(a.getSnapshot().value).toBe('open');
    clock.increment(1);
    expect(a.getSnapshot().value).toBe('alarm');
  });

  it('close cancels the timer', () => {
    const { clock, a } = start();
    a.send({ type: 'open' });
    clock.increment(20_000);
    a.send({ type: 'close' });
    clock.increment(100_000);
    expect(a.getSnapshot().value).toBe('closed');
  });

  it('reopen restarts the timer', () => {
    const { clock, a } = start();
    a.send({ type: 'open' });
    clock.increment(20_000);
    a.send({ type: 'close' });
    a.send({ type: 'open' });
    clock.increment(20_000);
    expect(a.getSnapshot().value).toBe('open');
    clock.increment(10_000);
    expect(a.getSnapshot().value).toBe('alarm');
  });
});

describe('history (fsm/docs/history.md)', () => {
  const resumeAfterAgitate = (history: HistoryKind) =>
    run(washer, ['start', 'filled', 'soaked', 'pause', 'resume'], { history }).value;

  it('deep history restores the exact leaf', () => {
    expect(resumeAfterAgitate('deep')).toEqual({ running: { wash: 'agitate' } });
  });

  it('shallow history restores wash at its default child', () => {
    expect(resumeAfterAgitate('shallow')).toEqual({ running: { wash: 'soak' } });
  });

  it('no history restarts at fill', () => {
    expect(resumeAfterAgitate('none')).toEqual({ running: 'fill' });
  });

  it.each(['deep', 'shallow'] as const)('%s history restores a simple child', (history) => {
    const s = run(washer, ['start', 'filled', 'soaked', 'washed', 'pause', 'resume'], { history });
    expect(s.value).toEqual({ running: 'spin' });
  });

  it('stop from paused', () => {
    expect(run(washer, ['start', 'pause', 'stop'], { history: 'deep' }).value).toBe('off');
  });
});

describe('parallel (fsm/docs/parallel.md)', () => {
  const styles = (events: string[]) => [...run(textStyle, events).tags].sort();

  it('starts with everything off', () => expect(styles([])).toEqual([]));

  it('toggles are independent', () => {
    expect(styles(['toggle_bold'])).toEqual(['BOLD']);
    expect(styles(['toggle_bold', 'toggle_underline'])).toEqual(['BOLD', 'UNDERLINE']);
    expect(styles(['toggle_bold', 'toggle_underline', 'toggle_bold'])).toEqual(['UNDERLINE']);
  });
});

describe('Moore vs Mealy (fsm/docs/moore-mealy.md)', () => {
  const outputs = (bits: number[]) => {
    const a = createActor(elevenDetector).start();
    return bits.map((b) => {
      a.send({ type: b ? 'one' : 'zero' });
      const s = a.getSnapshot();
      return { mealy: s.context.mealyOut, moore: s.hasTag('OUT') ? 1 : 0 };
    });
  };

  it('0110111 -> 0010011 for both', () => {
    const out = outputs([0, 1, 1, 0, 1, 1, 1]);
    expect(out.map((o) => o.mealy)).toEqual([0, 0, 1, 0, 0, 1, 1]);
    expect(out.map((o) => o.moore)).toEqual([0, 0, 1, 0, 0, 1, 1]);
  });

  it('equivalence is proven exhaustively over the product (3 states)', () => {
    const r = explore(elevenDetector, elevenDetectorSpec);
    expect(r.invariantViolations).toEqual([]);
    expect(r.stateCount).toBe(3);
  });

  it('a broken Moore machine is caught with a counterexample', () => {
    // Moore output on b instead of c: fires after a single 1.
    const broken = createMachine({
      ...(elevenDetector.config as object),
      states: {
        ...(elevenDetector.config.states as object),
        moore: {
          initial: 'a',
          states: {
            a: { on: { zero: { target: 'a' }, one: { target: 'b' } } },
            b: { tags: ['OUT'], on: { zero: { target: 'a' }, one: { target: 'c' } } },
            c: { on: { zero: { target: 'a' }, one: { target: 'c' } } },
          },
        },
      },
    } as never).provide(elevenDetector.implementations as never);
    const r = explore(broken, { ...elevenDetectorSpec, machine: broken } as never);
    expect(r.invariantViolations[0]?.path.events).toEqual(['one']);
  });
});
