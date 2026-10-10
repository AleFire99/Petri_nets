import type { AnyStateMachine } from 'xstate';
import { doorAlarm } from '../machines/doorAlarm.machine';
import { elevenDetector } from '../machines/elevenDetector.machine';
import { mediaPlayer } from '../machines/mediaPlayer.machine';
import { trafficLight, turnstile } from '../machines/regular.machine';
import { textStyle } from '../machines/textStyle.machine';
import { type VendingEvent, vendingMachine } from '../machines/vendingMachine.machine';
import { type HistoryKind, washer } from '../machines/washer.machine';
import type { MachineSpec } from './types';

/** One spec per design in docs/fsm/. Every design: nonblocking, deadlock-free, all states reachable. */

type Spec = MachineSpec<AnyStateMachine>;
const ok = { deadlocks: 0, blocking: 0 };
const ev = (...types: string[]) => types.map((type) => ({ type }));

// docs/fsm/regular.md
export const trafficLightSpec: MachineSpec<typeof trafficLight> = {
  slug: 'traffic-light',
  name: 'trafficLight (regular)',
  machine: trafficLight,
  events: ev('next') as never,
  marked: (s) => s.matches('red'),
  invariants: { 'exactly one lamp': (s) => s.tags.size === 1 },
  expect: ok,
};

export const turnstileSpec: MachineSpec<typeof turnstile> = {
  slug: 'turnstile',
  name: 'turnstile (regular)',
  machine: turnstile,
  events: ev('coin', 'push') as never,
  marked: (s) => s.matches('locked'),
  invariants: { 'released only when unlocked': (s) => s.hasTag('RELEASE') === s.matches('unlocked') },
  expect: ok,
};

// docs/fsm/hierarchical.md
export const mediaPlayerSpec: MachineSpec<typeof mediaPlayer> = {
  slug: 'media-player',
  name: 'mediaPlayer (hierarchical)',
  machine: mediaPlayer,
  events: ev('power_on', 'power_off', 'play', 'pause', 'stop') as never,
  marked: (s) => s.matches('off'),
  invariants: { 'audio only while playing': (s) => s.hasTag('AUDIO') === s.matches({ on: 'playing' }) },
  expect: ok,
};

// docs/fsm/extended.md
const coins: VendingEvent[] = [0, 25, 50, 100].map((amount) => ({ type: 'insert', amount }));
export const vendingSpec: MachineSpec<typeof vendingMachine> = {
  slug: 'vending-machine',
  name: 'vendingMachine (extended)',
  machine: vendingMachine,
  events: [...coins, { type: 'select' }, { type: 'refund' }],
  marked: (s) => s.matches('idle'),
  invariants: {
    'credit never negative': (s) => s.context.credit >= 0,
    'idle means no credit': (s) => !s.matches('idle') || s.context.credit === 0,
    'has_credit means credit > 0': (s) => !s.matches('has_credit') || s.context.credit > 0,
  },
  maxDepth: 4, // credit and counters are unbounded
  expect: ok,
};

// docs/fsm/timed.md
export const doorAlarmSpec: MachineSpec<typeof doorAlarm> = {
  slug: 'door-alarm',
  name: 'doorAlarm (timed)',
  machine: doorAlarm,
  events: ev('open', 'close') as never,
  marked: (s) => s.matches('closed'),
  invariants: { 'siren only in alarm': (s) => s.hasTag('SIREN') === s.matches('alarm') },
  expect: ok,
};

// docs/fsm/history.md
export const washerSpec = (history: HistoryKind): MachineSpec<typeof washer> => ({
  slug: `washer-${history}`,
  name: `washer (history: ${history})`,
  machine: washer,
  input: { history },
  events: ev('start', 'filled', 'soaked', 'washed', 'pause', 'resume', 'stop') as never,
  marked: (s) => s.matches('off'),
  invariants: { 'drum and valve never together': (s) => !(s.hasTag('DRUM') && s.hasTag('VALVE')) },
  expect: ok,
});

// docs/fsm/parallel.md
export const textStyleSpec: MachineSpec<typeof textStyle> = {
  slug: 'text-style',
  name: 'textStyle (parallel)',
  machine: textStyle,
  events: ev('toggle_bold', 'toggle_italic', 'toggle_underline') as never,
  marked: (s) => s.tags.size === 0,
  invariants: {},
  expect: ok,
};

// docs/fsm/moore-mealy.md
export const elevenDetectorSpec: MachineSpec<typeof elevenDetector> = {
  slug: 'eleven-detector',
  name: 'elevenDetector (Moore vs Mealy)',
  machine: elevenDetector,
  events: ev('zero', 'one') as never,
  marked: (s) => s.matches({ mealy: 's0', moore: 'a' }),
  invariants: {
    'Moore and Mealy outputs agree': (s) => s.context.mealyOut === (s.hasTag('OUT') ? 1 : 0),
  },
  expect: ok,
};

export const designSpecs: Spec[] = [
  trafficLightSpec,
  turnstileSpec,
  mediaPlayerSpec,
  vendingSpec,
  doorAlarmSpec,
  washerSpec('deep'),
  washerSpec('shallow'),
  washerSpec('none'),
  textStyleSpec,
  elevenDetectorSpec,
] as Spec[];
