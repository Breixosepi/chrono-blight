from typing import Any
from src.states.hazard.HazardBaseState import HazardBaseState


class RisingState(HazardBaseState):
    state_name: str = "rising"

    def enter(self, *args: Any, **kwargs: Any) -> None:
        self.hazard.alert_text = "¡EL LÍQUIDO SUBE!"
        self.hazard.alert_timer = 2.0
        self.hazard.room.camera.shake(3.0, 0.2)
        self.hazard.gate_current_y = self.hazard.gate_closed_y

    def update_with_player(self, dt: float, player: Any) -> None:
        if player.hitbox.top <= self.hazard.escape_y or player.hitbox.bottom <= (self.hazard.escape_y + 16.0):
            self.state_machine.change("escaped")
            return

        self.hazard.current_y = max(self.hazard.escape_y, self.hazard.current_y - self.hazard.speed * dt)
