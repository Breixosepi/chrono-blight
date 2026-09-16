"""
Chrono Blight - EnemyPatrolState
"""
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState
class EnemyPatrolState(EnemyBaseState):
    def enter(self, *args, **kwargs) -> None:
        enemy = self.entity
        enemy.change_animation("walk")
        
        if enemy.vx == 0.0:
            enemy.vx = enemy.walk_speed if enemy.facing == "right" else -enemy.walk_speed

    def update(self, dt: float) -> None:
        enemy = self.entity

        player_detected = (
            enemy.is_active() 
            and self.is_player_alive() 
            and enemy.distance_to_player() <= enemy.detect_range
        )
        
        if player_detected:
            self.change_state("chase")
            return

        if enemy.vx == 0.0:
            enemy.vx = enemy.walk_speed if enemy.facing == "right" else -enemy.walk_speed

        if enemy.facing == "right":
            if enemy.hitbox.x >= enemy.spawn_x + enemy.patrol_dist:
                enemy.vx = -enemy.walk_speed
                enemy.facing = "left"
        else:
            if enemy.hitbox.x <= enemy.spawn_x:
                enemy.vx = enemy.walk_speed
                enemy.facing = "right"

        enemy.change_animation("walk")