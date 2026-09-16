from typing import Any, Optional
from gale.timer import Timer, Tween, After
from src.states.hazard.HazardBaseState import HazardBaseState

class TriggeredState(HazardBaseState):
    def __init__(self, hazard: Any, state_machine: Any) -> None:
        super().__init__(hazard, state_machine)
        self.drop_tween: Optional[Tween] = None
        self.alarm_timer: Optional[After] = None

    def enter(self, *args: Any, **kwargs: Any) -> None:
        hazard = self.hazard
        hazard.alert_text = getattr(hazard, "triggered_text", "¡TRAMPA ACTIVADA!")
        hazard.alert_timer = hazard.delay_max
        hazard.room.camera.shake(3.5, 0.2)
        
        self.drop_tween = Timer.tween(
            0.22,
            [(hazard, {"gate_current_y": hazard.gate_closed_y})],
            ease_function_name="in_quad",
            on_finish=self._on_gate_landed,
        )
        self.alarm_timer = Timer.after(hazard.delay_max, self._start_moving)

    def _on_gate_landed(self) -> None:
        hazard = self.hazard
        hazard.gate_landed = True
        hazard.room.camera.shake(4.0, 0.25)
        hazard.spawn_gate_impact_particles()

    def _start_moving(self) -> None:
        self.state_machine.change("moving") 

    def exit(self) -> None:
        if self.drop_tween: self.drop_tween.remove()
        if self.alarm_timer: self.alarm_timer.remove()