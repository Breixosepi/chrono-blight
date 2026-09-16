"""
Chrono Blight - EnemyAttackState
"""
import random
import pygame
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState

class EnemyAttackState(EnemyBaseState):
    def enter(self, *args, **kwargs) -> None:
        enemy = self.entity
        self.attack_timer: float = 0.0
        self.damage_dealt: bool = False
        enemy.vx = 0.0

        if enemy.player is not None:
            direction = enemy.player_direction()
            enemy.facing = "right" if direction > 0 else "left"

        self._melee_hitbox = pygame.Rect(0, 0, 0, 0)
        self._select_and_start_attack()

    def _select_and_start_attack(self) -> None:
        enemy = self.entity

        if enemy.enemy_type == "big_monster":
            self.current_attack_name = "attack"
            enemy.change_animation("attack")
            self._spawn_boss_vines()

        elif enemy.enemy_type == "monster2":
            distance_to_player = enemy.horizontal_distance_to_player()
            if distance_to_player > 36.0:
                self.current_attack_name = "attack2"
            else:
                self.current_attack_name = random.choice(["attack", "attack2"])
            enemy.change_animation(self.current_attack_name)

        else:
            possible_attacks = ["attack", "attack2"]
            available_attacks = [name for name in possible_attacks if name in enemy.animations]
            self.current_attack_name = (
                random.choice(available_attacks) if available_attacks else "attack"
            )
            enemy.change_animation(self.current_attack_name)

    def _execute_projectile_attack(self, damage: int) -> None:
        enemy = self.entity
        self.damage_dealt = True
        enemy.spawn_projectile(speed=150.0, damage=damage)

    def _check_melee_hit(self, reach: int, damage: int) -> None:
        enemy = self.entity
        player = enemy.player
        if player is None or not enemy.is_active():
            return

        hitbox_width = reach
        hitbox_height = enemy.hitbox.height + 8
        hitbox_top = enemy.hitbox.top - 4

        if enemy.facing == "right":
            hitbox_left = enemy.hitbox.right - 2
        else:
            hitbox_left = enemy.hitbox.left - reach + 2

        self._melee_hitbox.update(hitbox_left, hitbox_top, hitbox_width, hitbox_height)

        if self._melee_hitbox.colliderect(player.hitbox) or enemy.hitbox.colliderect(player.hitbox):
            player.take_damage(damage, source_x=enemy.hitbox.centerx)
            self.damage_dealt = True

    def update(self, dt: float) -> None:
        enemy = self.entity
        if not self.is_player_alive():
            self.change_state("patrol")
            return

        self.attack_timer += dt
        if self.attack_timer < 0.2 and enemy.player is not None:
            direction = enemy.player_direction()
            enemy.facing = "right" if direction > 0 else "left"

        enemy.vx = 0.0

        action_def = enemy.get_action(self.current_attack_name)
        window_start, window_end = action_def.get("timing", enemy.attack_timing)
        reach_distance = int(action_def.get("reach", enemy.attack_reach))
        damage_amount = int(action_def.get("damage", enemy.contact_damage))

        if action_def.get("is_projectile") and self.attack_timer >= window_start and not self.damage_dealt:
            self._execute_projectile_attack(damage_amount)
        elif (
            not action_def.get("is_projectile")
            and not action_def.get("is_spell")
            and window_start <= self.attack_timer <= window_end
            and not self.damage_dealt
        ):
            self._check_melee_hit(reach_distance, damage_amount)

        if enemy.is_animation_finished(fallback_duration=enemy.attack_duration):
            enemy.vx = 0.0
            if self.is_player_alive() and enemy.distance_to_player() <= enemy.detect_range:
                self.change_state("chase", cooldown=enemy.attack_cooldown)
            else:
                self.change_state("patrol")

    def _spawn_boss_vines(self) -> None:
        enemy = self.entity
        if enemy.player is None:
            return

        target_center_x = float(enemy.player.hitbox.centerx)
        pattern = random.choice([0, 1, 2])

        if pattern == 0:
            target_positions = [target_center_x]
        elif pattern == 1:
            mid_x = (enemy.hitbox.centerx + target_center_x) / 2.0
            target_positions = [mid_x, target_center_x]
        else:
            step = (target_center_x - enemy.hitbox.centerx) / 3.0
            target_positions = [
                enemy.hitbox.centerx + step,
                enemy.hitbox.centerx + 2.0 * step,
                target_center_x,
            ]

        base_y = float(enemy.player.hitbox.bottom if enemy.player is not None else enemy.hitbox.bottom)
        variant_names = ["2a", "2b", "2c"]

        for index, vine_x in enumerate(target_positions):
            variant = variant_names[index % len(variant_names)] if len(target_positions) > 1 else "2c"
            enemy.hazards.append({
                "x": vine_x - 24.0,
                "y": base_y - 48.0,
                "timer": 0.0,
                "duration": 1.6,
                "interval": 0.10,
                "variant": variant,
                "damage": 18,
                "hitbox": pygame.Rect(int(vine_x - 12), int(base_y - 32), 24, 32),
                "resolved": False,
                "hit": False,
                "miss": False,
            })