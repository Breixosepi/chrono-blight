"""
Chrono Blight - EnemyChaseState
"""
import random
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState


class EnemyChaseState(EnemyBaseState):
    def enter(self, *args, **kwargs) -> None:
        enemy = self.entity
        self.jump_cooldown: float = 0.0
        self.attack_cooldown: float = kwargs.get("cooldown", 0.0)
        enemy.change_animation("walk")

    def update(self, dt: float) -> None:
        enemy = self.entity

        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if not enemy.is_active() or not self.is_player_alive() or enemy.distance_to_player() > enemy.detect_range:
            self.change_state("patrol")
            return

        distance_to_player = enemy.distance_to_player()
        direction = enemy.player_direction()
        enemy.facing = "right" if direction > 0 else "left"

        is_ranged_enemy = (enemy.enemy_type == "monster2")

        if is_ranged_enemy:
            min_keep_distance = 68.0
            if distance_to_player < min_keep_distance:
                enemy.vx = -enemy.walk_speed * 1.15 * direction
                if enemy.on_ground:
                    enemy.change_animation("walk")
            elif distance_to_player <= enemy.attack_range:
                enemy.vx = 0.0
                if self.attack_cooldown <= 0:
                    self.change_state("attack")
                    return
                elif enemy.on_ground:
                    enemy.change_animation("idle")
            else:
                enemy.vx = enemy.walk_speed * direction
                if enemy.on_ground:
                    enemy.change_animation("walk")
            return

        if distance_to_player <= enemy.attack_range:
            if self.attack_cooldown <= 0:
                self.change_state("attack")
                return
            else:
                enemy.vx = 0.0
                if enemy.on_ground:
                    enemy.change_animation("idle")
                return

        enemy.vx = enemy.walk_speed * direction

        can_jump = getattr(enemy, "can_jump", False) or ("jump" in enemy.animations)
        if can_jump and enemy.on_ground and self.jump_cooldown <= 0:
            delta_y = enemy.player.hitbox.centery - enemy.hitbox.centery
            delta_x = abs(enemy.hitbox.centerx - enemy.player.hitbox.centerx)
            
            if delta_y < -18.0 and delta_x <= min(enemy.detect_range * 0.85, 90.0):
                enemy.vy = getattr(enemy, "jump_velocity", -240.0)
                enemy.on_ground = False
                self.jump_cooldown = random.uniform(1.2, 1.8)
                if "jump" in enemy.animations:
                    enemy.change_animation("jump")

        if not enemy.on_ground and "jump" in enemy.animations:
            enemy.change_animation("jump")
        elif enemy.on_ground:
            enemy.change_animation("walk")