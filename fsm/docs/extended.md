# Extended FSM (guards + context)

Adds context variables, guard conditions on transitions and actions that update the context. The state set stays small while behaviour depends on data.

## Use case
Vending machine with `credit` (cents) and a fixed `price = 75`.

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> HasCredit: insert [credit += amount]
    HasCredit --> HasCredit: insert [credit += amount]
    HasCredit --> Idle: select [credit == price] / dispense, credit = 0
    HasCredit --> HasCredit: select [credit > price] / dispense, credit -= price
    HasCredit --> HasCredit: select [credit < price] / rejected
    HasCredit --> Idle: refund / credit = 0
```

| From | Event | Guard | Action | To |
|------|-------|-------|--------|----|
| Idle | insert(amount) | amount > 0 | credit += amount | HasCredit |
| HasCredit | insert(amount) | amount > 0 | credit += amount | HasCredit |
| HasCredit | select | credit >= price | credit -= price; dispense | Idle if credit == 0 else HasCredit |
| HasCredit | select | credit < price | none | HasCredit |
| HasCredit | refund | — | credit = 0 | Idle |

## In XState
Machine: [`vendingMachine.machine.ts`](../xstate/src/machines/vendingMachine.machine.ts) (vendingMachine). Scenario tests: [`designs.unit.test.ts`](../xstate/test/designs.unit.test.ts). Guard blocks under-funded purchase; change retained after purchase; refund zeroes credit. Checked (bounded, 4 events deep, coins 0/25/50/100): credit never negative, idle means no credit, `has_credit` means credit > 0.
