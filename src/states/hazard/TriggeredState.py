from typing import Any, Optional
from gale.timer import Timer, Tween, After
from src.states.hazard.HazardBaseState import HazardBaseState


class TriggeredState(HazardBaseState):
    state_name: str = "triggered"

    def __init__(self, hazard: Any, state_machine: Any) -> None:
        super().__init__(hazard, state_machine)
        self.drop_tween: Optional[Tween] = None
        self.alarm_timer: Optional[After] = None

    def enter(self, *args: Any, **kwargs: Any) -> None:
        self.hazard.alert_text = "¡TRAMPA ACTIVADA!"
        self.hazard.alert_timer = self.hazard.delay_max
        self.hazard.room.camera.shake(3.5, 0.2)

        self.drop_tween = Timer.tween(
            0.22,
            [(self.hazard, {"gate_current_y": self.hazard.gate_closed_y})],
            ease_function_name="in_quad",
            on_finish=self._on_gate_landed,
        )
        self.alarm_timer = Timer.after(self.hazard.delay_max, self._start_rising)

    def _on_gate_landed(self) -> None:
        self.hazard.gate_landed = True
        self.hazard.room.camera.shake(4.0, 0.25)
        self.hazard.spawn_gate_impact_particles()

    def _start_rising(self) -> None:
        self.state_machine.change("rising")

    def exit(self) -> None:
        if self.drop_tween is not None:
            self.drop_tween.remove()
            self.drop_tween = None
        if self.alarm_timer is not None:
            self.alarm_timer.remove()
            self.alarm_timer = None

