"""
Chrono Blight
"""

from src.states.entity.enemy.EnemyBaseState import EnemyBaseState

KNOCKBACK_SPEED: float = 80.0
HIT_DURATION: float = 0.35


class EnemyHitState(EnemyBaseState):
    has_gravity: bool = True

    def enter(self, *args, **kwargs) -> None:

        e = self.entity
        e.change_animation("hit")
        self._timer: float = 0.0

        if e.player is not None:
            direction = 1 if e.hitbox.centerx >= e.player.hitbox.centerx else -1
        else:
            direction = 1 if e.facing == "right" else -1
        e.vx = KNOCKBACK_SPEED * direction

    def update(self, dt: float) -> None:
        e = self.entity
        self._timer += dt
        e.vx *= max(0.0, 1.0 - dt * 8.0)

        if e.is_animation_finished(fallback_duration=HIT_DURATION):
            e.vx = 0.0
            if e.is_active() and self.is_player_alive() and e.distance_to_player() <= e.detect_range:
                self.change_state("chase")
            else:
                self.change_state("patrol")

