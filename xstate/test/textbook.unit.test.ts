import { describe, expect, it } from 'vitest';
import { SimulatedClock, createActor } from 'xstate';
import { DOOR_TIMEOUT_MS, doorAlarm } from '../src/machines/doorAlarm.machine';
import { vendingMachine } from '../src/machines/vendingMachine.machine';

/** Same scenarios as tests/fsm/test_timed.py and tests/fsm/test_extended.py, in XState. */

describe('doorAlarm (cf. tests/fsm/test_timed.py)', () => {
  const start = () => {
    const clock = new SimulatedClock();
    return { clock, actor: createActor(doorAlarm, { clock }).start() };
  };

  it('no alarm before timeout, alarm at timeout', () => {
    const { clock, actor } = start();
    actor.send({ type: 'open' });
    clock.increment(DOOR_TIMEOUT_MS - 1000);
    expect(actor.getSnapshot().value).toBe('open');
    clock.increment(1000);
    expect(actor.getSnapshot().value).toBe('alarm');
  });

  it('reopen restarts the timer', () => {
    const { clock, actor } = start();
    actor.send({ type: 'open' });
    clock.increment(20_000);
    actor.send({ type: 'close' });
    actor.send({ type: 'open' });
    clock.increment(20_000);
    expect(actor.getSnapshot().value).toBe('open');
    clock.increment(10_000);
    expect(actor.getSnapshot().value).toBe('alarm');
  });
});

describe('vendingMachine (cf. tests/fsm/test_extended.py)', () => {
  const start = () => createActor(vendingMachine).start();

  it('underfunded select is rejected', () => {
    const a = start();
    a.send({ type: 'insert', amount: 50 });
    a.send({ type: 'select' });
    const s = a.getSnapshot();
    expect([s.value, s.context.credit, s.context.dispensed, s.context.rejected]).toEqual(['has_credit', 50, 0, 1]);
  });

  it('change is retained after purchase', () => {
    const a = start();
    a.send({ type: 'insert', amount: 100 });
    a.send({ type: 'select' });
    expect([a.getSnapshot().value, a.getSnapshot().context.credit]).toEqual(['has_credit', 25]);
  });

  it('non-positive insert is ignored (Python raises TransitionNotAllowed)', () => {
    const a = start();
    a.send({ type: 'insert', amount: 0 });
    expect([a.getSnapshot().value, a.getSnapshot().context.credit]).toEqual(['idle', 0]);
  });
});
