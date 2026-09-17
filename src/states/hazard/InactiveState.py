from typing import Any
from src.states.hazard.HazardBaseState import HazardBaseState

class InactiveState(HazardBaseState):
    def enter(self, *args: Any, **kwargs: Any) -> None:
        hazard = self.hazard
        hazard.current_y = getattr(hazard, "inactive_y", float(hazard.room.MAP_HEIGHT))
        hazard.alert_text = ""
        hazard.alert_timer = 0.0
        hazard.liquid_particles.clear()

    def update_with_player(self, dt: float, player: Any) -> None:
        hazard = self.hazard
        if hazard.trigger_rect and hazard.trigger_rect.colliderect(player.hitbox):
            self.state_machine.change("triggered")