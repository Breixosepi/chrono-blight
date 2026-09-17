from typing import Any, Optional
from gale.timer import Timer, After
from src.states.hazard.HazardBaseState import HazardBaseState

class TriggeredState(HazardBaseState):
    def __init__(self, hazard: Any, state_machine: Any) -> None:
        super().__init__(hazard, state_machine)
        self.alarm_timer: Optional[After] = None

    def enter(self, *args: Any, **kwargs: Any) -> None:
        hazard = self.hazard
        hazard.alert_text = getattr(hazard, "triggered_text", "¡TRAMPA ACTIVADA!")
        hazard.alert_timer = hazard.delay_max
        hazard.room.camera.shake(3.5, 0.2)
        self.alarm_timer = Timer.after(hazard.delay_max, self._start_moving)

    def _start_moving(self) -> None:
        self.state_machine.change("moving") 

    def exit(self) -> None:
        if self.alarm_timer: self.alarm_timer.remove()