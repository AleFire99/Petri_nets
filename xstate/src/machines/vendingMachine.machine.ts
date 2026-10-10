import { assign, setup } from 'xstate';

/**
 * Vending machine. Same design as docs/fsm/extended.md and
 * src/petrilab/fsm/extended.py (python-statemachine). State ids and context
 * names match the Python implementation so test vectors replay 1:1.
 */
export const PRICE = 75;

export type VendingEvent =
  | { type: 'insert'; amount: number }
  | { type: 'select' }
  | { type: 'refund' };

export const vendingMachine = setup({
  types: {
    context: {} as { credit: number; dispensed: number; rejected: number },
    events: {} as VendingEvent,
  },
  guards: {
    positive: ({ event }) => event.type === 'insert' && event.amount > 0,
    exact: ({ context }) => context.credit === PRICE,
    enough: ({ context }) => context.credit >= PRICE,
  },
  actions: {
    addCredit: assign({
      credit: ({ context, event }) => context.credit + (event.type === 'insert' ? event.amount : 0),
    }),
    dispense: assign({
      credit: ({ context }) => context.credit - PRICE,
      dispensed: ({ context }) => context.dispensed + 1,
    }),
    reject: assign({ rejected: ({ context }) => context.rejected + 1 }),
    clearCredit: assign({ credit: 0 }),
  },
}).createMachine({
  id: 'vendingMachine',
  initial: 'idle',
  context: { credit: 0, dispensed: 0, rejected: 0 },
  states: {
    idle: {
      on: { insert: { guard: 'positive', target: 'has_credit', actions: 'addCredit' } },
    },
    has_credit: {
      on: {
        insert: { guard: 'positive', target: 'has_credit', actions: 'addCredit' },
        select: [
          { guard: 'exact', target: 'idle', actions: 'dispense' },
          { guard: 'enough', target: 'has_credit', actions: 'dispense' },
          { target: 'has_credit', actions: 'reject' },
        ],
        refund: { target: 'idle', actions: 'clearCredit' },
      },
    },
  },
});
