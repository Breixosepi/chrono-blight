from typing import Any
from src.states.hazard.HazardBaseState import HazardBaseState


class InactiveState(HazardBaseState):
    state_name: str = "inactive"

    def enter(self, *args: Any, **kwargs: Any) -> None:
        self.hazard.current_y = float(self.hazard.room.MAP_HEIGHT)
        self.hazard.gate_current_y = self.hazard.gate_open_y
        self.hazard.gate_landed = False
        self.hazard.alert_text = ""
        self.hazard.alert_timer = 0.0
        self.hazard.liquid_particles.clear()

    def update_with_player(self, dt: float, player: Any) -> None:
        if player.hitbox.centerx >= self.hazard.trigger_x and player.hitbox.bottom >= 550:
            self.state_machine.change("triggered")

