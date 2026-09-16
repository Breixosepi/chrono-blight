"""
Chrono Blight - EscapedState
"""
from typing import Any
from src.states.hazard.HazardBaseState import HazardBaseState

class EscapedState(HazardBaseState):
    state_name: str = "escaped"

    def enter(self, *args: Any, **kwargs: Any) -> None:
        hazard = self.hazard
        hazard.alert_text = getattr(hazard, "escaped_text", "¡ESCAPASTE!")
        hazard.alert_timer = getattr(hazard, "escaped_timer_duration", 5.0)
        
        if hasattr(hazard, "room") and hasattr(hazard.room, "camera"):
            hazard.room.camera.shake(2.5, 0.2)

    def update_with_player(self, dt: float, player: Any) -> None:
        pass