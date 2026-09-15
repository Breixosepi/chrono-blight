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
        direction = e.player_direction()
        e.facing = "right" if direction > 0 else "left"

        # Comportamiento táctico de tirador a distancia para monster2 (pistolero)
        is_ranged = (e.enemy_type == "monster2")
        if is_ranged:
            min_keep_dist = 68.0
            if dist < min_keep_dist:
                # El jugador se acercó demasiado: huir en dirección opuesta (manteniendo la vista en él)
                e.vx = -e.walk_speed * 1.15 * direction
                if e.on_ground:
                    e.change_animation("walk")
            elif dist <= e.attack_range:
                # En rango óptimo de tiro: detenerse y disparar si está listo
                e.vx = 0.0
                if self.attack_cooldown <= 0:
                    self.change_state("attack")
                    return
                elif e.on_ground:
                    e.change_animation("idle")
            else:
                # Demasiado lejos: avanzar para entrar en rango de disparo
                e.vx = e.walk_speed * direction
                if e.on_ground:
                    e.change_animation("walk")
            return

        # Comportamiento cuerpo a cuerpo estándar
        if dist <= e.attack_range:
            if self.attack_cooldown <= 0:
                self.change_state("attack")
                return
            else:
                e.vx = 0.0
                if e.on_ground:
                    e.change_animation("idle")
                return

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

