"""
Chrono Blight - EnemyDeathState
"""
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState


class EnemyDeathState(EnemyBaseState):
    def enter(self, *args, **kwargs) -> None:
        enemy = self.entity
        enemy.change_animation("death")
        enemy.vx = 0.0
        self.death_duration = getattr(enemy, "death_duration", 1.0)

    def update(self, dt: float) -> None:
        enemy = self.entity
        enemy.vx = 0.0
        
        if enemy.is_animation_finished(fallback_duration=self.death_duration):
            enemy.dead = True