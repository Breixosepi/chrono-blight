"""
Chrono Blight
"""

import math
import random
import pygame
from src.states.entity.enemy.EnemyBaseState import EnemyBaseState


class EnemyAttackState(EnemyBaseState):
    def enter(self, *args, **kwargs) -> None:
        e = self.entity
        self.has_gravity = (e.float_amplitude == 0.0)
        self._attack_timer: float = 0.0
        self._damage_dealt: bool = False
        e.vx = 0.0

        if e.player is not None:
            direction = e.player_direction()
            e.facing = "right" if direction > 0 else "left"

        if e.enemy_type == "big_monster":
            self._current_attack = "attack"
            e.change_animation("attack")
            self._spawn_boss_vines()
        else:
            possible = ["attack", "attack2"]
            available = [k for k in possible if k in e.animations]
            self._current_attack = random.choice(available) if available else "attack"
            e.change_animation(self._current_attack)

    def update(self, dt: float) -> None:
        e = self.entity

        if not self.is_player_alive():
            self.change_state("patrol")
            return

        # Floating oscillation (e.g. monster_eyes)
        if e.float_amplitude > 0:
            e.float_timer += dt
            e.y = e.spawn_y + math.sin(e.float_timer * e.float_speed * math.pi) * e.float_amplitude
            e.hitbox.y = int(e.y)
            e.vy = 0.0

        self._attack_timer += dt

        if self._attack_timer < 0.2 and e.player is not None:
            direction = e.player_direction()
            e.facing = "right" if direction > 0 else "left"

        e.vx = 0.0

        curr_atk = getattr(self, "_current_attack", "attack")
        action = e.get_action(curr_atk)
        t_start, t_end = action.get("timing", e.attack_timing)
        reach = int(action.get("reach", e.attack_reach))
        dmg = int(action.get("damage", e.contact_damage))

        if t_start <= self._attack_timer <= t_end and not self._damage_dealt and e.player is not None:
            if e.is_active():
                if e.facing == "right":
                    atk_rect = pygame.Rect(e.hitbox.right - 2, e.hitbox.top - 4, reach, e.hitbox.height + 8)
                else:
                    atk_rect = pygame.Rect(e.hitbox.left - reach + 2, e.hitbox.top - 4, reach, e.hitbox.height + 8)

                if atk_rect.colliderect(e.player.hitbox) or e.hitbox.colliderect(e.player.hitbox):
                    attack_func = action.get("func")
                    if attack_func:
                        attack_func(e, e.player, curr_atk)
                    else:
                        e.player.take_damage(dmg, source_x=e.hitbox.centerx)
                    self._damage_dealt = True

        if e.is_animation_finished(fallback_duration=e.attack_duration):
            e.vx = 0.0
            if self.is_player_alive() and e.distance_to_player() <= e.detect_range:
                self.change_state("chase", cooldown=e.attack_cooldown)
            else:
                self.change_state("patrol")

    def _spawn_boss_vines(self) -> None:
        e = self.entity
        if e.player is None:
            return

        target_x = float(e.player.hitbox.centerx)
        pattern = random.choice([0, 1, 2])
        if pattern == 0:
            targets = [target_x]
        elif pattern == 1:
            mid_x = (e.hitbox.centerx + target_x) / 2.0
            targets = [mid_x, target_x]
        else:
            step = (target_x - e.hitbox.centerx) / 3.0
            targets = [
                e.hitbox.centerx + step,
                e.hitbox.centerx + 2.0 * step,
                target_x,
            ]

        variants = ["2a", "2b", "2c"]
        for idx, tx in enumerate(targets):
            var = variants[idx % len(variants)] if len(targets) > 1 else "2c"
            hazard = {
                "x": tx - 24.0,
                "y": float(e.floor_y - 48),
                "timer": 0.0,
                "duration": 1.6,
                "interval": 0.10,
                "variant": var,
                "damage": 18,
                "hitbox": pygame.Rect(int(tx - 12), int(e.floor_y - 32), 24, 32),
                "resolved": False,
                "hit": False,
                "miss": False,
            }
            e.hazards.append(hazard)

