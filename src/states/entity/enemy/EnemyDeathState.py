"""
Chrono Blight
"""

from src.states.entity.enemy.EnemyBaseState import EnemyBaseState

DEATH_DURATION: float = 1.0


class EnemyDeathState(EnemyBaseState):
    has_gravity: bool = True

    def enter(self, *args, **kwargs) -> None:
        e = self.entity
        e.change_animation("death")
        e.vx = 0.0
        self._timer: float = 0.0

    def update(self, dt: float) -> None:
        e = self.entity
        self._timer += dt
        e.vx = 0.0

        if e.is_animation_finished(fallback_duration=DEATH_DURATION):
            e.dead = True

