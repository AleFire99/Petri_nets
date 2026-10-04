"""Extended FSM (guards + context): vending machine. See docs/fsm/extended.md."""

from statemachine import State, StateChart


class VendingMachine(StateChart):
    allow_event_without_transition = False
    catch_errors_as_events = False

    price = 75

    idle = State(initial=True)
    has_credit = State()

    insert = idle.to(has_credit, cond="positive") | has_credit.to.itself(
        cond="positive"
    )
    select = (
        has_credit.to(idle, cond="exact")
        | has_credit.to.itself(cond="enough")
        | has_credit.to.itself(unless="enough")
    )
    refund = has_credit.to(idle)

    def __init__(self) -> None:
        self.credit = 0
        self.dispensed = 0
        self.rejected = 0
        super().__init__()

    def positive(self, amount: int) -> bool:
        return amount > 0

    def exact(self) -> bool:
        return self.credit == self.price

    def enough(self) -> bool:
        return self.credit >= self.price

    def on_insert(self, amount: int) -> None:
        self.credit += amount

    def on_select(self) -> None:
        if self.enough():
            self.credit -= self.price
            self.dispensed += 1
        else:
            self.rejected += 1

    def on_refund(self) -> None:
        self.credit = 0
