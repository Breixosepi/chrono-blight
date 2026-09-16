"""
Chrono Blight - EnemyHitState
"""
from gale.timer import Timer
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState


class EnemyHitState(EnemyBaseState):
    def enter(self, *args, **kwargs) -> None:
        enemy = self.entity
        enemy.change_animation("hit")

        knockback = getattr(enemy, "knockback_speed", 80.0)
        self.hit_duration = getattr(enemy, "hit_duration", 0.35)

        if enemy.player is not None:
            direction = 1.0 if enemy.hitbox.centerx >= enemy.player.hitbox.centerx else -1.0
        else:
            direction = 1.0 if enemy.facing == "right" else -1.0

        enemy.vx = knockback * direction

        Timer.tween(
            self.hit_duration,
            [(enemy, {"vx": 0.0})],
            ease_function_name="out_quad"
        )

    def update(self, dt: float) -> None:
        enemy = self.entity

        if enemy.is_animation_finished(fallback_duration=self.hit_duration):
            enemy.vx = 0.0
            player_in_range = (
                enemy.is_active() 
                and self.is_player_alive() 
                and enemy.distance_to_player() <= enemy.detect_range
            )
            
            if player_in_range:
                self.change_state("chase")
            else:
                self.change_state("patrol")