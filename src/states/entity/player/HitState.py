"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState


class HitState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("hit")
        self.duration = 0.25

    def update(self, dt: float) -> None:
        self.entity.vx *= max(0.0, 1.0 - dt * 6.0)

        if self.entity.is_animation_finished(fallback_duration=self.duration):
            if self.entity.on_ground:
                self.change_state("idle")
            else:
                self.change_state("fall")

