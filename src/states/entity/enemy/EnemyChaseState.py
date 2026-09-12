"""
Chrono Blight
"""

import math
import random
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState


class EnemyChaseState(EnemyBaseState):

    def enter(self, *args, **kwargs) -> None:
        e = self.entity
        self.has_gravity = (e.float_amplitude == 0.0)
        self.jump_cooldown: float = 0.0
        self.attack_cooldown: float = kwargs.get("cooldown", 0.0)

        e.change_animation("walk")

    def update(self, dt: float) -> None:
        e = self.entity

        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Floating oscillation (e.g. monster_eyes)
        if e.float_amplitude > 0:
            e.float_timer += dt
            e.y = e.spawn_y + math.sin(e.float_timer * e.float_speed * math.pi) * e.float_amplitude
            e.hitbox.y = int(e.y)
            e.vy = 0.0

        if not e.is_active() or not self.is_player_alive() or e.distance_to_player() > e.detect_range:
            self.change_state("patrol")
            return

        dist = e.distance_to_player()

        if dist <= e.attack_range:
            if self.attack_cooldown <= 0:
                self.change_state("attack")
                return
            else:
                e.vx = 0.0
                direction = e.player_direction()
                e.facing = "right" if direction > 0 else "left"
                if e.on_ground:
                    e.change_animation("idle")
                return

        direction = e.player_direction()
        e.facing = "right" if direction > 0 else "left"
        e.vx = e.walk_speed * direction

        # Jump behavior 
        can_jump = getattr(e, "can_jump", False) or ("jump" in e.animations)
        if can_jump and e.float_amplitude == 0.0 and e.on_ground and self.jump_cooldown <= 0:
            dy = e.player.hitbox.centery - e.hitbox.centery
            dx = abs(e.hitbox.centerx - e.player.hitbox.centerx)

            if dy < -18.0 and dx <= min(e.detect_range * 0.85, 90.0):
                e.vy = getattr(e, "jump_velocity", -240.0)
                e.on_ground = False
                self.jump_cooldown = random.uniform(1.2, 1.8)
                if "jump" in e.animations:
                    e.change_animation("jump")

        if not e.on_ground and "jump" in e.animations:
            e.change_animation("jump")
        elif e.on_ground:
            e.change_animation("walk")

