from typing import Any
from src.states.hazard.HazardBaseState import HazardBaseState


class EscapedState(HazardBaseState):
    state_name: str = "escaped"

    def enter(self, *args: Any, **kwargs: Any) -> None:
        self.hazard.alert_text = "¡ESCAPASTE!"
        self.hazard.alert_timer = 5.0
        self.hazard.room.camera.shake(2.5, 0.2)

    def update_with_player(self, dt: float, player: Any) -> None:
        pass

