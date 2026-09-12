"""
Chrono Blight
"""

import math
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState


class EnemyPatrolState(EnemyBaseState):

    def enter(self, *args, **kwargs) -> None:
        e = self.entity
        self.has_gravity = (e.float_amplitude == 0.0)
        e.change_animation("walk")

        if e.vx == 0.0:
            e.vx = e.walk_speed if e.facing == "right" else -e.walk_speed

    def update(self, dt: float) -> None:
        e = self.entity

        # Floating oscillation (e.g. monster_eyes)
        if e.float_amplitude > 0:
            e.float_timer += dt
            e.y = e.spawn_y + math.sin(e.float_timer * e.float_speed * math.pi) * e.float_amplitude
            e.hitbox.y = int(e.y)
            e.vy = 0.0

        if e.is_active() and self.is_player_alive() and e.distance_to_player() <= e.detect_range:
            self.change_state("chase")
            return

        if e.vx == 0.0:
            e.vx = e.walk_speed if e.facing == "right" else -e.walk_speed

        if e.facing == "right":
            if e.hitbox.x >= e.spawn_x + e.patrol_dist:
                e.vx = -e.walk_speed
                e.facing = "left"
        else:
            if e.hitbox.x <= e.spawn_x:
                e.vx = e.walk_speed
                e.facing = "right"

        e.change_animation("walk")
