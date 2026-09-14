from typing import Any
from gale.state import BaseState, StateMachine


class HazardBaseState(BaseState):
    state_name: str = "base"

    def __init__(self, hazard: Any, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.hazard = hazard

    def update_with_player(self, dt: float, player: Any) -> None:
        pass

