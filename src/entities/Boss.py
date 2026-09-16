"""
Chrono Blight — Boss
"""
from __future__ import annotations

import math
from typing import Any

import pygame
from gale.state import StateMachine

import settings
from src.definitions import entity as entity_defs
from src.entities.Enemy import Enemy
from src.states.entity.boss.BossBaseState import BossBaseState
from src.states.entity.boss.BossIdleState import BossIdleState
from src.states.entity.enemy.EnemyHitState import EnemyHitState
from src.states.entity.enemy.EnemyDeathState import EnemyDeathState
from src.states.entity.boss.cultist.CultistChaseState import CultistChaseState
from src.states.entity.boss.cultist.CultistAttackState import CultistAttackState
from src.states.entity.boss.lurker.LurkerIdleState import LurkerIdleState
from src.states.entity.boss.lurker.LurkerAttackState import LurkerAttackState


class Boss(Enemy):

    def __init__(
        self,
        x: float,
        y: float,
        enemy_type: str,
        floor_y: float = 160.0,
        map_w: float = 1248.0,
    ) -> None:
        _originally_missing = enemy_type not in entity_defs.ENEMY_DEFS
        if _originally_missing and enemy_type in entity_defs.BOSS_DEFS:
            entity_defs.ENEMY_DEFS[enemy_type] = entity_defs.BOSS_DEFS[enemy_type]

        super().__init__(x, y, enemy_type, floor_y=floor_y, map_w=map_w)

        if _originally_missing and enemy_type in entity_defs.ENEMY_DEFS:
            del entity_defs.ENEMY_DEFS[enemy_type]

        boss_states = {
            "idle":   lambda sm: BossIdleState(self, sm),
            "patrol": lambda sm: BossIdleState(self, sm),
            "hit":    lambda sm: EnemyHitState(self, sm),
            "death":  lambda sm: EnemyDeathState(self, sm),
        }

        if enemy_type == "cultist_priest":
            boss_states["chase"] = lambda sm: CultistChaseState(self, sm)
            boss_states["attack"] = lambda sm: CultistAttackState(self, sm)
        elif enemy_type == "monster2_boss":
            boss_states["idle"] = lambda sm: LurkerIdleState(self, sm)
            boss_states["attack"] = lambda sm: LurkerAttackState(self, sm)

        self.state_machine = StateMachine(boss_states)
        self.change_state("idle")

        self.is_boss: bool = True
        self.boss_phase: int = 1
        self.shield_active: bool = False
        self.shield_pulse: float = 0.0

        self.ground_shockwaves: list[dict] = []
        self.void_orbs: list[dict] = []
        self.burst_hazards: list[dict] = []
        self.side_shoots: list[dict] = []

        self._sw_frames: list[pygame.Surface] = settings.FRAMES.get("ground_shockwave_frames", [])
        self._orb_frames: list[pygame.Surface] = settings.FRAMES.get("void_orb_frames", [])
        self._burst_frames: list[pygame.Surface] = settings.FRAMES.get("burst_frames", [])
        self._side_shoot_frames: list[pygame.Surface] = settings.FRAMES.get("side_shoot_frames", [])
        self._sw_anim_timer: float = 0.0
        self._orb_anim_timer: float = 0.0
        self._EFFECT_FPS: float = 1.0 / 12.0

    # ------------------------------------------------------------------
    # Spawn de habilidades
    # ------------------------------------------------------------------

    def spawn_ground_shockwave(
        self,
        sx: float,
        base_y: float,
        direction: float,
        speed: float = 160.0,
        damage: int = 14,
    ) -> None:
        self.ground_shockwaves.append({
            "x":         sx,
            "base_y":    base_y,
            "vx":        speed * direction,
            "direction": direction,
            "damage":    damage,
            "life":      2.2,
            "anim_t":    0.0,
            "state":     "spawn",  # spawn, travel, despawn
            "resolved":  False,
        })

    def spawn_void_orb(
        self,
        sx: float,
        sy: float,
        target_x: float,
        target_y: float,
        speed: float = 85.0,
        damage: int = 16,
    ) -> None:
        dx = target_x - sx
        dy = target_y - sy
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            dx, dy = 1.0, 0.0
            dist = 1.0
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed
        self.void_orbs.append({
            "x":        sx,
            "y":        sy,
            "vx":       vx,
            "vy":       vy,
            "speed":    speed,
            "damage":   damage,
            "life":     5.0,   
            "anim_t":   0.0,
            "state":    "spawn", 
            "resolved": False,
            "trail":    [],
        })

    def spawn_burst(
        self,
        target_x: float,
        target_y: float,
        damage: int = 14,
    ) -> None:
        self.burst_hazards.append({
            "x": target_x,
            "y": target_y,
            "damage": damage,
            "timer": 0.0,
            "state": "warning",
            "resolved": False,
        })

    def spawn_side_shoot(
        self,
        y: float,
        direction: float,
        start_x: float,
        speed: float = 160.0,
        damage: int = 10,
    ) -> None:
        self.side_shoots.append({
            "x": start_x,
            "y": y,
            "direction": direction,
            "vx": speed * direction,
            "damage": damage,
            "anim_t": 0.0,
            "life": 4.5,
            "resolved": False,
        })


    def update(self, dt: float) -> None:
        if self.shield_active:
            self.shield_pulse += dt * 4.0

        map_w = float(getattr(self, "map_w", settings.VIRTUAL_WIDTH))

        # Actualizar ondas de choque terrestres
        for sw in self.ground_shockwaves[:]:
            sw["anim_t"] += dt

            if sw["state"] == "spawn":
                sw["x"] += sw["vx"] * dt * 0.1  # Mueve muy despacio mientras nace
                if sw["anim_t"] >= 5 * self._EFFECT_FPS:
                    sw["state"] = "travel"
                    sw["anim_t"] = 0.0
            elif sw["state"] == "travel":
                sw["life"] -= dt
                sw["x"] += sw["vx"] * dt

                # Despawn si se acaba el tiempo o sale del mapa
                if sw["life"] <= 0 or sw["x"] <= 16.0 or sw["x"] >= map_w - 16.0:
                    sw["state"] = "despawn"
                    sw["anim_t"] = 0.0
            elif sw["state"] == "despawn":
                if sw["anim_t"] >= 5 * self._EFFECT_FPS:
                    if sw in self.ground_shockwaves:
                        self.ground_shockwaves.remove(sw)

            # Colisión con jugador (activa durante spawn y travel)
            if sw["state"] in ("spawn", "travel"):
                player = self.player
                is_sword_special = (player is not None and player.state_name == "attack_special" and player.skin == "sword")
                sw_rect = pygame.Rect(int(sw["x"] - 14), int(sw["base_y"] - 48), 28, 48)
                if (
                    self.is_active()
                    and player is not None
                    and not player.is_dead()
                    and player.state_name not in ("hit", "death", "dash")
                    and not is_sword_special
                    and player.invulnerable_timer <= 0.0
                    and not sw["resolved"]
                    and sw_rect.colliderect(player.hitbox)
                ):
                    sw["resolved"] = True
                    sw["state"] = "despawn"
                    sw["anim_t"] = 0.0
                    player.take_damage(int(sw["damage"]), source_x=sw["x"])
                    if self.on_hazard_hit:
                        self.on_hazard_hit({"damage": sw["damage"], "hitbox": sw_rect})

        # Actualizar orbes del vacío flotantes
        for orb in self.void_orbs[:]:
            orb["anim_t"] += dt
            orb["trail"].append({"x": orb["x"], "y": orb["y"], "life": 0.18})
            for tr in orb["trail"][:]:
                tr["life"] -= dt
                if tr["life"] <= 0:
                    orb["trail"].remove(tr)

            if orb["state"] == "spawn":
                if orb["anim_t"] >= 5 * self._EFFECT_FPS:
                    orb["state"] = "travel"
                    orb["anim_t"] = 0.0
            elif orb["state"] == "travel":
                orb["life"] -= dt
                orb["x"] += orb["vx"] * dt
                orb["y"] += orb["vy"] * dt

                # Homing logic (persigue al jugador)
                player = self.player
                if player is not None and not player.is_dead():
                    dx = player.hitbox.centerx - orb["x"]
                    dy = player.hitbox.centery - orb["y"]
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        target_vx = (dx / dist) * orb["speed"]
                        target_vy = (dy / dist) * orb["speed"]
                        orb["vx"] += (target_vx - orb["vx"]) * dt * 2.0
                        orb["vy"] += (target_vy - orb["vy"]) * dt * 2.0

                if orb["life"] <= 0 or orb["x"] <= 16.0 or orb["x"] >= map_w - 16.0:
                    orb["state"] = "despawn"
                    orb["anim_t"] = 0.0
            elif orb["state"] == "despawn":
                if orb["anim_t"] >= 5 * self._EFFECT_FPS:
                    if orb in self.void_orbs:
                        self.void_orbs.remove(orb)

            # Colisión con jugador (activa durante spawn y travel)
            if orb["state"] in ("spawn", "travel"):
                player = self.player
                is_sword_special = (player is not None and player.state_name == "attack_special" and player.skin == "sword")
                orb_rect = pygame.Rect(int(orb["x"] - 12), int(orb["y"] - 12), 24, 24)
                if (
                    self.is_active()
                    and player is not None
                    and not player.is_dead()
                    and player.state_name not in ("hit", "death", "dash")
                    and not is_sword_special
                    and player.invulnerable_timer <= 0.0
                    and not orb["resolved"]
                    and orb_rect.colliderect(player.hitbox)
                ):
                    orb["resolved"] = True
                    orb["state"] = "despawn"
                    orb["anim_t"] = 0.0
                    player.take_damage(int(orb["damage"]), source_x=orb["x"])
                    if self.on_hazard_hit:
                        self.on_hazard_hit({"damage": orb["damage"], "hitbox": orb_rect})

        for b in self.burst_hazards[:]:
            b["timer"] += dt
            if b["state"] == "warning":
                if b["timer"] >= 1.0:
                    b["state"] = "damage"
                    b["timer"] = 0.0
            elif b["state"] == "damage":
                if not b["resolved"]:
                    player = self.player
                    is_sword_special = (player is not None and player.state_name == "attack_special" and player.skin == "sword")
                    b_rect = pygame.Rect(int(b["x"] - 24), int(b["y"] - 24), 48, 48)
                    if (
                        self.is_active()
                        and player is not None
                        and not player.is_dead()
                        and player.state_name not in ("hit", "death", "dash")
                        and not is_sword_special
                        and player.invulnerable_timer <= 0.0
                        and b_rect.colliderect(player.hitbox)
                    ):
                        b["resolved"] = True
                        player.take_damage(int(b["damage"]), source_x=b["x"])
                        if self.on_hazard_hit:
                            self.on_hazard_hit({"damage": b["damage"], "hitbox": b_rect})
                if b["timer"] >= 1.0:
                    if b in self.burst_hazards:
                        self.burst_hazards.remove(b)

        for s in self.side_shoots[:]:
            s["anim_t"] += dt
            s["x"] += s["vx"] * dt
            s["life"] -= dt
            
            player = self.player
            is_sword_special = (player is not None and player.state_name == "attack_special" and player.skin == "sword")
            s_rect = pygame.Rect(int(s["x"] - 16), int(s["y"] - 16), 32, 32)
            if (
                self.is_active()
                and player is not None
                and not player.is_dead()
                and player.state_name not in ("hit", "death", "dash")
                and not is_sword_special
                and player.invulnerable_timer <= 0.0
                and not s["resolved"]
                and s_rect.colliderect(player.hitbox)
            ):
                s["resolved"] = True
                player.take_damage(int(s["damage"]), source_x=s["x"])
                if self.on_hazard_hit:
                    self.on_hazard_hit({"damage": s["damage"], "hitbox": s_rect})
                if s in self.side_shoots:
                    self.side_shoots.remove(s)
                continue

            if s["life"] <= 0 or s["x"] < -100.0 or s["x"] > map_w + 100.0:
                if s in self.side_shoots:
                    self.side_shoots.remove(s)

        super().update(dt)

    def render(
        self,
        surface: pygame.Surface,
        camera_x: float = 0.0,
        camera_y: float = 0.0,
    ) -> None:
        # --- Onda de choque terrestre con sprite ---
        sw_frames = self._sw_frames
        for sw in self.ground_shockwaves:
            if not sw_frames:
                # Fallback: elipse simple si no hay sprite cargado
                sx = int(sw["x"] - camera_x)
                sy = int(sw["base_y"] - camera_y)
                fb = pygame.Surface((28, 22), pygame.SRCALPHA)
                pygame.draw.ellipse(fb, (160, 20, 120, 210), (0, 0, 28, 22))
                surface.blit(fb, (sx - 14, sy - 20))
                continue

            # Selección de frames por estado
            if sw["state"] == "spawn":
                frame_idx = min(4, int(sw["anim_t"] / self._EFFECT_FPS))
            elif sw["state"] == "travel":
                # Looping middle frames (5 to 8)
                frame_idx = 5 + int(sw["anim_t"] / self._EFFECT_FPS) % 4
            else:
                # Despawn frames (9 to 13)
                frame_idx = 9 + min(4, int(sw["anim_t"] / self._EFFECT_FPS))

            frame_idx = min(frame_idx, len(sw_frames) - 1)
            sw_surf = sw_frames[frame_idx]

            # Flip si el shockwave va hacia la izquierda
            if sw["direction"] < 0:
                sw_surf = pygame.transform.flip(sw_surf, True, False)

            sx = int(sw["x"] - camera_x) - sw_surf.get_width() // 2
            sy = int(sw["base_y"] - camera_y) - sw_surf.get_height()
            surface.blit(sw_surf, (sx, sy))

        # --- Orbe del vacío con sprite ---
        orb_frames = self._orb_frames
        for orb in self.void_orbs:
            # Estela dibujada en pygame.draw (ligera, no necesita sprite)
            for tr in orb.get("trail", []):
                tx = int(tr["x"] - camera_x)
                ty = int(tr["y"] - camera_y)
                t_alpha = int(160 * (tr["life"] / 0.18))
                t_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, (190, 40, 180, t_alpha), (5, 5), 4)
                surface.blit(t_surf, (tx - 5, ty - 5))

            if not orb_frames:
                # Fallback: círculo simple
                ox = int(orb["x"] - camera_x)
                oy = int(orb["y"] - camera_y)
                fb = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(fb, (240, 60, 200, 200), (10, 10), 9)
                surface.blit(fb, (ox - 10, oy - 10))
                continue

            if orb["state"] == "spawn":
                frame_idx = min(4, int(orb["anim_t"] / self._EFFECT_FPS))
            elif orb["state"] == "travel":
                # Looping middle frames (5 to 9)
                frame_idx = 5 + int(orb["anim_t"] / self._EFFECT_FPS) % 5
            else:
                # Despawn frames (10 to 14)
                frame_idx = 10 + min(4, int(orb["anim_t"] / self._EFFECT_FPS))

            frame_idx = min(frame_idx, len(orb_frames) - 1)
            orb_surf = orb_frames[frame_idx]
            ox = int(orb["x"] - camera_x) - orb_surf.get_width() // 2
            oy = int(orb["y"] - camera_y) - orb_surf.get_height() // 2
            surface.blit(orb_surf, (ox, oy))

        burst_frames = self._burst_frames
        for b in self.burst_hazards:
            if burst_frames and len(burst_frames) >= 16:
                if b["state"] == "warning":
                    f_idx = min(3, int((b["timer"] / 1.0) * 4))
                else:
                    f_idx = 4 + min(11, int((b["timer"] / 1.0) * 12))
                
                f_idx = min(f_idx, len(burst_frames) - 1)
                b_surf = burst_frames[f_idx]
                bx = int(b["x"] - camera_x) - b_surf.get_width() // 2
                by = int(b["y"] - camera_y) - b_surf.get_height() // 2
                surface.blit(b_surf, (bx, by))

        side_frames = self._side_shoot_frames
        for s in self.side_shoots:
            if side_frames:
                f_idx = int(s["anim_t"] / 0.08) % len(side_frames)
                s_surf = side_frames[f_idx]
                if s["direction"] < 0:
                    s_surf = pygame.transform.flip(s_surf, True, False)
                sx = int(s["x"] - camera_x) - s_surf.get_width() // 2
                sy = int(s["y"] - camera_y) - s_surf.get_height() // 2
                surface.blit(s_surf, (sx, sy))

        super().render(surface, camera_x, camera_y)

    def take_damage(self, amount: float) -> None:
        if not self.is_active():
            return
        if self.shield_active or getattr(self, "invulnerable", False):
            self.hit_flash_timer = 0.15
            return
        if self.state_name == "death":
            return
        self._health = max(0.0, self._health - amount)
        self.hit_flash_timer = 0.25
        if self._health <= 0.0:
            self.change_state("death")
        else:
            self.change_state("hit")
