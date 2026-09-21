"""
Chrono Blight — Boss
"""
from __future__ import annotations

import math
import random
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
        elif enemy_type == "the_harvester":
            from src.states.entity.boss.harvester.HarvesterIdleState import HarvesterIdleState
            from src.states.entity.boss.harvester.HarvesterWalkState import HarvesterWalkState
            from src.states.entity.boss.harvester.HarvesterAttackState import HarvesterAttackState
            from src.states.entity.boss.harvester.HarvesterStunState import HarvesterStunState
            from src.states.entity.boss.harvester.HarvesterDashState import HarvesterDashState
            from src.states.entity.boss.harvester.HarvesterHitState import HarvesterHitState
            boss_states["idle"] = lambda sm: HarvesterIdleState(self, sm)
            boss_states["patrol"] = lambda sm: HarvesterWalkState(self, sm)
            boss_states["walk"] = lambda sm: HarvesterWalkState(self, sm)
            boss_states["chase"] = lambda sm: HarvesterWalkState(self, sm)
            boss_states["attack"] = lambda sm: HarvesterAttackState(self, sm)
            boss_states["stun"] = lambda sm: HarvesterStunState(self, sm)
            boss_states["dash"] = lambda sm: HarvesterDashState(self, sm)
            boss_states["hit"] = lambda sm: HarvesterHitState(self, sm)

        self.state_machine = StateMachine(boss_states)
        self.change_state("idle")

        self._harvester_hit_counter: int = 0
        self._harvester_hit_window: float = 0.0

        self.is_boss: bool = True
        self.boss_phase: int = 1
        self.shield_active: bool = False
        self.shield_pulse: float = 0.0

        self.ground_shockwaves: list[dict] = []
        self.void_orbs: list[dict] = []
        self.burst_hazards: list[dict] = []
        self.side_shoots: list[dict] = []
        self.wind_blades: list[dict] = []
        self.falling_blades: list[dict] = []
        self.dimensional_slashes: list[dict] = []
        self._p3_teleporting: bool = False

        self._sw_frames: list[pygame.Surface] = settings.FRAMES.get("ground_shockwave_frames", [])
        self._orb_frames: list[pygame.Surface] = settings.FRAMES.get("void_orb_frames", [])
        self._burst_frames: list[pygame.Surface] = settings.FRAMES.get("burst_frames", [])
        self._side_shoot_frames: list[pygame.Surface] = settings.FRAMES.get("side_shoot_frames", [])
        self._wb_green_frames: list[pygame.Surface] = settings.FRAMES.get("wind_blade_green_frames", [])
        self._wb_red_frames: list[pygame.Surface] = settings.FRAMES.get("wind_blade_red_frames", [])
        self._wb_green_h: list[pygame.Surface] = settings.FRAMES.get("wind_blade_green_horiz", [])
        self._wb_green_v: list[pygame.Surface] = settings.FRAMES.get("wind_blade_green_vert", [])
        self._wb_red_h: list[pygame.Surface] = settings.FRAMES.get("wind_blade_red_horiz", [])
        self._wb_red_v: list[pygame.Surface] = settings.FRAMES.get("wind_blade_red_vert", [])
        self._exp_slash_green: list[pygame.Surface] = settings.FRAMES.get("explosion_slash_green_frames", [])
        self._exp_burst_green: list[pygame.Surface] = settings.FRAMES.get("explosion_burst_green_frames", [])
        self._exp_slash_red: list[pygame.Surface] = settings.FRAMES.get("explosion_slash_red_frames", [])
        self._exp_burst_red: list[pygame.Surface] = settings.FRAMES.get("explosion_burst_red_frames", [])
        self._sw_anim_timer: float = 0.0
        self._orb_anim_timer: float = 0.0
        self._EFFECT_FPS: float = 1.0 / 12.0

    def teleport_to(self, tx: float, ty: float) -> None:
        old_x, old_y = self.x, self.y
        self.x = float(tx)
        self.y = float(ty)
        self.hitbox.topleft = (int(self.x), int(self.y))
        self.vx = 0.0
        self.vy = 0.0
        if self.room:
            self.room.spawn_dust(old_x + self.width // 2, old_y + self.height, count=10)
            self.room.spawn_dust(self.x + self.width // 2, self.y + self.height, count=12)
            self.room.camera.shake(2.5, 0.15)
        if "change" in settings.SOUNDS:
            settings.SOUNDS["change"].play()

    def _schedule_p3_chase_teleport(self) -> None:
        if getattr(self, "_p3_teleporting", False):
            return
        self._p3_teleporting = True

        def _do_teleport():
            self._p3_teleporting = False
            if self.health <= 0 or self.state_name == "death":
                return
            px = self.player.hitbox.centerx if self.player else 800.0
            platforms = [
                (785.0, 85.0),
                (295.0, 101.0),
                (1255.0, 101.0),
                (672.0, 133.0),
                (896.0, 133.0),
                (200.0, 53.0),
                (1350.0, 53.0),
            ]
            far_plats = [p for p in platforms if abs(p[0] - px) >= 260]
            if not far_plats:
                far_plats = platforms
            import random
            target = random.choice(far_plats)
            self.teleport_to(target[0], target[1])
            self.change_state("attack")

        from gale.timer import Timer
        Timer.after(0.20, _do_teleport)

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

    def spawn_wind_blade(
        self,
        sx: float,
        sy: float,
        direction: float,
        phase_color: str = "green",
        is_vertical: bool = False,
        speed: float = 210.0,
        damage: int = 12,
    ) -> None:
        self.wind_blades.append({
            "x": sx,
            "y": sy,
            "vx": speed * direction,
            "direction": direction,
            "phase_color": phase_color,
            "is_vertical": is_vertical,
            "damage": damage,
            "life": 4.0,
            "anim_t": 0.0,
            "resolved": False,
        })

    def spawn_falling_blade(
        self,
        target_x: float,
        phase_color: str = "green",
        delay: float = 0.45,
        damage: int = 14,
    ) -> None:
        self.falling_blades.append({
            "target_x": target_x,
            "phase_color": phase_color,
            "delay": delay,
            "timer": 0.0,
            "y": -40.0,
            "vy": 420.0,
            "state": "warning",
            "anim_t": 0.0,
            "damage": damage,
            "resolved": False,
        })

    def spawn_dimensional_slash(
        self,
        target_x: float,
        target_y: float,
        phase_color: str = "red",
        delay: float = 0.8,
        damage: int = 16,
    ) -> None:
        self.dimensional_slashes.append({
            "x": target_x,
            "y": target_y,
            "phase_color": phase_color,
            "delay": delay,
            "timer": 0.0,
            "state": "slash",
            "anim_t": 0.0,
            "damage": damage,
            "resolved": False,
        })


    def update(self, dt: float) -> None:
        if self.shield_active:
            self.shield_pulse += dt * 4.0

        map_w = float(getattr(self, "map_w", settings.VIRTUAL_WIDTH))

        # Actualizar ondas de choque terrestres
        for sw in self.ground_shockwaves:
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
                    sw["is_dead"] = True

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
        for orb in self.void_orbs:
            orb["anim_t"] += dt
            orb["trail"].append({"x": orb["x"], "y": orb["y"], "life": 0.18})
            for tr in orb["trail"]:
                tr["life"] -= dt
            orb["trail"] = [tr for tr in orb["trail"] if tr["life"] > 0]

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
                    orb["is_dead"] = True

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

        for b in self.burst_hazards:
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
                    b["is_dead"] = True

        for s in self.side_shoots:
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
                s["is_dead"] = True
                continue

            if s["life"] <= 0 or s["x"] < -100.0 or s["x"] > map_w + 100.0:
                s["is_dead"] = True

        # Actualizar ondas de viento (wind_blades)
        for wb in self.wind_blades:
            wb["anim_t"] += dt
            wb["x"] += wb["vx"] * dt
            wb["life"] -= dt

            player = self.player
            if player is not None and not player.is_dead() and not wb["resolved"]:
                is_vert = wb.get("is_vertical", False)
                if is_vert:
                    # Tall vertical crescent: cannot jump over, must dash through
                    wb_rect = pygame.Rect(int(wb["x"] - 14), int(wb["y"] - 29), 28, 58)
                    jumped_over = False
                    dashed_through = (player.state_name == "dash")
                else:
                    # Low horizontal wave: can jump over
                    wb_rect = pygame.Rect(int(wb["x"] - 23), int(wb["y"] - 10), 46, 20)
                    jumped_over = (player.hitbox.bottom < wb["y"] - 4)
                    dashed_through = (player.state_name == "dash")

                is_sword_special = (player.state_name == "attack_special" and player.skin == "sword")

                if (
                    player.state_name not in ("hit", "death")
                    and not is_sword_special
                    and player.invulnerable_timer <= 0.0
                    and wb_rect.colliderect(player.hitbox)
                    and not jumped_over
                    and not dashed_through
                ):
                    wb["resolved"] = True
                    player.take_damage(int(wb["damage"]), source_x=wb["x"])
                    if self.on_hazard_hit:
                        self.on_hazard_hit({"damage": wb["damage"], "hitbox": wb_rect})
                    if self.room:
                        self.room.camera.shake(3.5, 0.18)
                        col = (80, 255, 120) if wb["phase_color"] == "green" else (255, 80, 80)
                        self.room._spawn_popup(f"-{int(wb['damage'])}", player.hitbox.centerx, player.hitbox.top - 10, 0.7, col)
                        self.room.spawn_dust(wb["x"], wb["y"], count=8)
                    wb["is_dead"] = True
                    continue

            if wb["life"] <= 0 or wb["x"] < -100.0 or wb["x"] > map_w + 100.0:
                wb["is_dead"] = True

        for ds in self.dimensional_slashes:
            ds["timer"] += dt
            ds["anim_t"] += dt

            if ds["state"] == "slash":
                if ds["timer"] >= ds["delay"]:
                    ds["state"] = "explode"
                    ds["timer"] = 0.0
                    ds["anim_t"] = 0.0
                    if "morph-fire" in settings.SOUNDS:
                        settings.SOUNDS["morph-fire"].play()
                    if self.room:
                        self.room.camera.shake(4.0, 0.25)
                        self.room.spawn_dust(ds["x"], ds["y"], count=12)

            elif ds["state"] == "explode":
                if not ds["resolved"]:
                    player = self.player
                    if player is not None and not player.is_dead():
                        exp_rect = pygame.Rect(int(ds["x"] - 28), int(ds["y"] - 28), 56, 56)
                        is_sword_special = (player.state_name == "attack_special" and player.skin == "sword")
                        if (
                            player.state_name not in ("hit", "death", "dash")
                            and not is_sword_special
                            and player.invulnerable_timer <= 0.0
                            and exp_rect.colliderect(player.hitbox)
                        ):
                            ds["resolved"] = True
                            player.take_damage(int(ds["damage"]), source_x=ds["x"])
                            if self.on_hazard_hit:
                                self.on_hazard_hit({"damage": ds["damage"], "hitbox": exp_rect})
                            if self.room:
                                self.room.camera.shake(4.0, 0.2)
                                col = (255, 80, 80) if ds["phase_color"] == "red" else (80, 255, 120)
                                self.room._spawn_popup(f"-{int(ds['damage'])}", player.hitbox.centerx, player.hitbox.top - 10, 0.7, col)

                if ds["timer"] >= 0.70:
                    ds["is_dead"] = True

        for fb in self.falling_blades:
            fb["timer"] += dt
            fb["anim_t"] += dt

            if fb["state"] == "warning":
                if fb["timer"] >= fb["delay"]:
                    fb["state"] = "falling"
                    fb["timer"] = 0.0
                    fb["y"] = -40.0
                    if "sword" in settings.SOUNDS:
                        settings.SOUNDS["sword"].play()
            elif fb["state"] == "falling":
                fb["y"] += fb["vy"] * dt

                player = self.player
                if player is not None and not player.is_dead() and not fb["resolved"]:
                    fb_rect = pygame.Rect(int(fb["target_x"] - 14), int(fb["y"] - 20), 28, 54)
                    is_sword_special = (player.state_name == "attack_special" and player.skin == "sword")
                    if (
                        player.state_name not in ("hit", "death", "dash")
                        and not is_sword_special
                        and player.invulnerable_timer <= 0.0
                        and fb_rect.colliderect(player.hitbox)
                    ):
                        fb["resolved"] = True
                        player.take_damage(int(fb["damage"]), source_x=fb["target_x"])
                        if self.on_hazard_hit:
                            self.on_hazard_hit({"damage": fb["damage"], "hitbox": fb_rect})
                        if self.room:
                            self.room.camera.shake(3.5, 0.18)
                            col = (80, 255, 120) if fb["phase_color"] == "green" else (255, 80, 80)
                            self.room._spawn_popup(f"-{int(fb['damage'])}", player.hitbox.centerx, player.hitbox.top - 10, 0.7, col)
                            self.room.spawn_dust(fb["target_x"], fb["y"], count=8)

                if fb["y"] >= 236.0:
                    fb["state"] = "impact"
                    if self.room:
                        self.room.camera.shake(2.5, 0.12)
                        self.room.spawn_dust(fb["target_x"], 238.0, count=8)
                    fb["is_dead"] = True

        # Limpieza consolidada por comprensión de listas (elimina .remove y copias en runtime)
        self.ground_shockwaves = [sw for sw in self.ground_shockwaves if not sw.get("is_dead")]
        self.void_orbs = [orb for orb in self.void_orbs if not orb.get("is_dead")]
        self.burst_hazards = [b for b in self.burst_hazards if not b.get("is_dead")]
        self.side_shoots = [s for s in self.side_shoots if not s.get("is_dead")]
        self.wind_blades = [wb for wb in self.wind_blades if not wb.get("is_dead")]
        self.dimensional_slashes = [ds for ds in self.dimensional_slashes if not ds.get("is_dead")]
        self.falling_blades = [fb for fb in self.falling_blades if not fb.get("is_dead")]

        super().update(dt)

        if self.enemy_type == "the_harvester":
            if getattr(self, "_harvester_hit_window", 0.0) > 0.0:
                self._harvester_hit_window = max(0.0, self._harvester_hit_window - dt)
                if self._harvester_hit_window <= 0.0:
                    self._harvester_hit_counter = 0

        # Harvester Phase 3 Aerial Safety: never walk/stay in acid/lava floor
        if getattr(self, "boss_phase", 1) == 3 and self.enemy_type == "the_harvester":
            if self.hitbox.bottom >= 220:
                self.teleport_to(785.0, 85.0)

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
                fb.fill((0, 0, 0, 0))
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
                t_surf.fill((0, 0, 0, 0))
                pygame.draw.circle(t_surf, (190, 40, 180, t_alpha), (5, 5), 4)
                surface.blit(t_surf, (tx - 5, ty - 5))

            if not orb_frames:
                ox = int(orb["x"] - camera_x)
                oy = int(orb["y"] - camera_y)
                fb = pygame.Surface((20, 20), pygame.SRCALPHA)
                fb.fill((0, 0, 0, 0))
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

        # --- Ondas de viento (wind_blades) ---
        for wb in self.wind_blades:
            is_vert = wb.get("is_vertical", False)
            color = wb.get("phase_color", "green")
            if is_vert:
                frames_list = self._wb_red_v if color == "red" else self._wb_green_v
            else:
                frames_list = self._wb_red_h if color == "red" else self._wb_green_h

            if frames_list:
                f_idx = int(wb["anim_t"] / 0.10) % len(frames_list)
                surf = frames_list[f_idx]
                
                # Orient facing movement direction
                if is_vert:
                    # In frame 4/6, convex cutting edge is on LEFT. If moving right (> 0), flip X!
                    if wb["direction"] > 0:
                        surf = pygame.transform.flip(surf, True, False)
                    # Radiant vertical aura to make it striking and visible
                    aura_col = (255, 60, 60, 65) if color == "red" else (60, 255, 120, 65)
                    aura_w, aura_h = surf.get_width() + 10, surf.get_height() + 10
                    aura_surf = pygame.Surface((aura_w, aura_h), pygame.SRCALPHA)
                    aura_surf.fill((0, 0, 0, 0))
                    pygame.draw.ellipse(aura_surf, aura_col, (0, 0, aura_w, aura_h))
                    ax = int(wb["x"] - camera_x) - aura_w // 2
                    ay = int(wb["y"] - camera_y) - aura_h // 2
                    surface.blit(aura_surf, (ax, ay))
                else:
                    # For horizontal: if moving left (< 0), flip X!
                    if wb["direction"] < 0:
                        surf = pygame.transform.flip(surf, True, False)

                wx = int(wb["x"] - camera_x) - surf.get_width() // 2
                wy = int(wb["y"] - camera_y) - surf.get_height() // 2
                surface.blit(surf, (wx, wy))

        # --- Cortes dimensionales explosivos (dimensional_slashes) ---
        for ds in self.dimensional_slashes:
            color = ds["phase_color"]
            if ds["state"] == "slash":
                slash_list = self._exp_slash_red if color == "red" else self._exp_slash_green
                if slash_list:
                    f_idx = min(len(slash_list) - 1, int(ds["anim_t"] / 0.12) % len(slash_list))
                    s_surf = slash_list[f_idx]
                    dx = int(ds["x"] - camera_x) - s_surf.get_width() // 2
                    dy = int(ds["y"] - camera_y) - s_surf.get_height() // 2
                    surface.blit(s_surf, (dx, dy))
            elif ds["state"] == "explode":
                burst_list = self._exp_burst_red if color == "red" else self._exp_burst_green
                if burst_list:
                    f_idx = min(len(burst_list) - 1, int(ds["anim_t"] / 0.07))
                    b_surf = burst_list[f_idx]
                    dx = int(ds["x"] - camera_x) - b_surf.get_width() // 2
                    dy = int(ds["y"] - camera_y) - b_surf.get_height() // 2
                    surface.blit(b_surf, (dx, dy))

        # --- Cortes que caen del cielo (falling_blades) ---
        for fb in self.falling_blades:
            color = fb["phase_color"]
            col_rgb = (255, 70, 70) if color == "red" else (60, 255, 130)
            tx = int(fb["target_x"] - camera_x)

            if fb["state"] == "warning":
                # Haz vertical de luz telegrafiado desde el cielo hasta el suelo
                alpha_pulse = int(45 + 35 * math.sin(fb["timer"] * 24))
                beam_surf = pygame.Surface((22, 300), pygame.SRCALPHA)
                beam_surf.fill((*col_rgb, alpha_pulse))
                pygame.draw.line(beam_surf, (*col_rgb, min(255, alpha_pulse * 2)), (11, 0), (11, 300), 2)
                surface.blit(beam_surf, (tx - 11, int(-camera_y)))
                # Retícula en el suelo
                ground_screen_y = int(238 - camera_y)
                pygame.draw.ellipse(surface, (*col_rgb, 200), (tx - 14, ground_screen_y - 6, 28, 12), 2)

            elif fb["state"] == "falling":
                # Estela de velocidad cayendo hacia abajo
                trail_h = 56
                trail_surf = pygame.Surface((16, trail_h), pygame.SRCALPHA)
                for ty in range(trail_h):
                    a = int(120 * (ty / trail_h))
                    pygame.draw.line(trail_surf, (*col_rgb, a), (0, ty), (16, ty))
                by = int(fb["y"] - camera_y)
                surface.blit(trail_surf, (tx - 8, by - trail_h))

                # Sprite de la hoja vertical cayendo en picada
                v_frames = self._wb_red_v if color == "red" else self._wb_green_v
                if v_frames:
                    f_idx = int(fb["anim_t"] / 0.08) % len(v_frames)
                    surf = v_frames[f_idx]
                    aura_w, aura_h = surf.get_width() + 10, surf.get_height() + 10
                    aura_surf = pygame.Surface((aura_w, aura_h), pygame.SRCALPHA)
                    aura_surf.fill((0, 0, 0, 0))
                    pygame.draw.ellipse(aura_surf, (*col_rgb, 75), (0, 0, aura_w, aura_h))
                    surface.blit(aura_surf, (tx - aura_w // 2, by - aura_h // 2))
                    surface.blit(surf, (tx - surf.get_width() // 2, by - surf.get_height() // 2))

        super().render(surface, camera_x, camera_y)

    def take_damage(self, amount: float) -> None:
        if not self.is_active():
            return
        if self.shield_active or getattr(self, "invulnerable", False):
            self.hit_flash_timer = 0.15
            if self.room:
                self.room._spawn_popup("ESCUDO", self.hitbox.centerx, self.hitbox.top - 8, 0.45, (220, 110, 255))
            return

        if self.state_name == "death":
            return
        self._health = max(0.0, self._health - amount)
        self.hit_flash_timer = 0.25
        if self._health <= 0.0:
            self.change_state("death")
        else:
            if self.enemy_type == "the_harvester":
                if getattr(self, "boss_phase", 1) == 3:
                    self._schedule_p3_chase_teleport()

                if self.state_name == "stun":
                    return

                if self.state_name in ("attack", "dash"):
                    return

                self._harvester_hit_counter = getattr(self, "_harvester_hit_counter", 0) + 1
                self._harvester_hit_window = 1.4

                if self._harvester_hit_counter >= 3:
                    self._harvester_hit_counter = 0
                    if random.random() < 0.60:
                        self.change_state("attack")
                    else:
                        self.change_state("dash")
                    return

                self.change_state("hit")
            elif self.state_name != "stun":
                self.change_state("hit")
