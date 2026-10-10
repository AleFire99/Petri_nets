import { describe, expect, it } from 'vitest';
import { SimulatedClock, createActor } from 'xstate';
import { MAX_RETRIES, TIMING, fillStation } from '../src/machines/fillStation.machine';

/**
 * Scenario tests. Real interpreter + SimulatedClock:
 * time only moves when the test says so. No sleeps, no flakiness.
 */
function start() {
  const clock = new SimulatedClock();
  const actor = createActor(fillStation, { clock }).start();
  return { actor, clock, snap: () => actor.getSnapshot() };
}

describe('fillStation scenarios', () => {
  it('runs a full batch: fill -> heat -> settle -> drain -> idle', () => {
    const { actor, clock, snap } = start();
    actor.send({ type: 'START' });
    expect(snap().value).toEqual({ running: 'filling' });
    expect(snap().hasTag('INLET')).toBe(true);

    actor.send({ type: 'LEVEL_HIGH' });
    expect(snap().hasTag('HEATER')).toBe(true);

    actor.send({ type: 'TEMP_OK' });
    expect(snap().value).toEqual({ running: 'settling' });

    clock.increment(TIMING.SETTLE_TIME - 1);
    expect(snap().value).toEqual({ running: 'settling' }); // not yet
    clock.increment(1);
    expect(snap().value).toEqual({ running: 'draining' });

    actor.send({ type: 'LEVEL_LOW' });
    expect(snap().value).toBe('idle');
  });

  it('faults when tank does not fill in time', () => {
    const { actor, clock, snap } = start();
    actor.send({ type: 'START' });
    clock.increment(TIMING.FILL_TIMEOUT);
    expect(snap().value).toBe('fault');
    expect(snap().context.lastFault).toBe('FILL_TIMEOUT');
  });

  it('timer is cancelled when state is left early', () => {
    const { actor, clock, snap } = start();
    actor.send({ type: 'START' });
    clock.increment(TIMING.FILL_TIMEOUT - 1000);
    actor.send({ type: 'LEVEL_HIGH' });
    clock.increment(2000); // old fill timeout would fire here
    expect(snap().value).toEqual({ running: 'heating' });
  });

  it(`locks out after ${MAX_RETRIES} retries, maintenance reset clears`, () => {
    const { actor, clock, snap } = start();
    for (let i = 0; i < MAX_RETRIES; i++) {
      actor.send({ type: 'START' });
      clock.increment(TIMING.FILL_TIMEOUT);
      actor.send({ type: 'RESET' });
      expect(snap().value).toBe('idle');
    }
    actor.send({ type: 'START' });
    clock.increment(TIMING.FILL_TIMEOUT);
    actor.send({ type: 'RESET' });
    expect(snap().value).toBe('lockedOut');

    actor.send({ type: 'MAINT_RESET' });
    expect(snap().value).toBe('idle');
    expect(snap().context.retries).toBe(0);
  });

  it('ESTOP from deep state kills all outputs', () => {
    const { actor, snap } = start();
    actor.send({ type: 'START' });
    actor.send({ type: 'LEVEL_HIGH' });
    actor.send({ type: 'ESTOP' });
    expect(snap().value).toBe('emergency');
    expect([...snap().tags]).toEqual([]);
  });
});
