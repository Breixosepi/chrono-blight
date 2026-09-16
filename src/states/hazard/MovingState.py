"""
Chrono Blight - MovingState
"""
from typing import Any
from gale.timer import Timer
from src.states.hazard.HazardBaseState import HazardBaseState

class MovingState(HazardBaseState):
    state_name: str = "moving"  

    def enter(self, *args: Any, **kwargs: Any) -> None:
        hazard = self.hazard
        hazard.alert_text = getattr(hazard, "moving_text", "¡EL LÍQUIDO SUBE!")
        hazard.alert_timer = 2.0
        
        if hasattr(hazard, "room") and hasattr(hazard.room, "camera"):
            hazard.room.camera.shake(3.0, 0.2)
            
        hazard.gate_current_y = hazard.gate_closed_y
        
        target_color = getattr(hazard, "target_color", None)
        if target_color:
            Timer.tween(2.0, [(hazard, {"color_r": target_color[0], "color_g": target_color[1], "color_b": target_color[2]})])

    def update_with_player(self, dt: float, player: Any) -> None:
        hazard = self.hazard
        velocity = getattr(hazard, "velocity_y", -hazard.speed) 

        escaped = False
        if velocity < 0:
            escaped = player.hitbox.top <= hazard.escape_y or player.hitbox.bottom <= (hazard.escape_y + 16.0)
        else: 
            escaped = player.hitbox.bottom >= hazard.escape_y

        if escaped:
            self.state_machine.change("escaped")
            return 

        hazard.current_y += velocity * dt

        if velocity < 0:
            hazard.current_y = max(hazard.escape_y, hazard.current_y)
        else:
            hazard.current_y = min(hazard.escape_y, hazard.current_y)