"""
Chrono Blight - HitState
"""
from gale.timer import Timer
from src.states.entity.EntityBaseState import EntityBaseState


class HitState(EntityBaseState):
    def enter(self) -> None:
        player = self.entity
        player.change_animation("hit")
        self.hit_duration = 0.25

        Timer.tween(
            self.hit_duration,
            [(player, {"vx": 0.0})],
            ease_function_name="out_quad"
        )

    def update(self, dt: float) -> None:
        player = self.entity
        
        if player.is_animation_finished(fallback_duration=self.hit_duration):
            if player.on_ground:
                self.change_state("idle")
            else:
                self.change_state("fall")