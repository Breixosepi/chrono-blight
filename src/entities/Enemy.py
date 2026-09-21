import math
import random
from typing import Any, Dict, Optional

import pygame
from gale.animation import Animation
from gale.state import StateMachine

import settings
from src.definitions import entity as entity_defs
from src.entities.Entity import Entity
from src.states.entity.enemy.EnemyPatrolState import EnemyPatrolState
from src.states.entity.enemy.EnemyChaseState import EnemyChaseState
from src.states.entity.enemy.EnemyAttackState import EnemyAttackState
from src.states.entity.enemy.EnemyHitState import EnemyHitState
from src.states.entity.enemy.EnemyDeathState import EnemyDeathState
from src.entities.Player import Player


class Enemy(Entity):
    """Base class for all Chrono Blight enemies."""

    GHOST_ALPHA: int = 65
    _flip_cache: Dict[int, pygame.Surface] = {}
    _ghost_cache: Dict[int, pygame.Surface] = {}
    _plasma_trail_surf: Optional[pygame.Surface] = None
    _plasma_bullet_surf: Optional[pygame.Surface] = None

    def __init__(
        self,
        x: float,
        y: float,
        enemy_type: str,
        floor_y: float = 160.0,
        map_w: float = 1248.0,
    ) -> None:
        defn = entity_defs.ENEMY_DEFS[enemy_type]
        self.defn: dict = defn
        hb = defn["hitbox"]

        super().__init__(
            x, y,
            width=hb["width"],
            height=hb["height"],
            floor_y=floor_y,
            map_w=map_w,
        )

        self.enemy_type: str = enemy_type
        self.phase: str = defn["phase"]

        # Render offset so the art is centred on the hitbox
        ro = defn["render_offset"]
        self.render_offset_x: int = ro["x"]
        self.render_offset_y: int = ro["y"]

        # Stats
        stats = defn["stats"]
        self._health: float = stats["max_health"]
        self._max_health: float = stats["max_health"]
        self.contact_damage: float = stats["contact_damage"]
        self.knockback_speed: float = stats.get("knockback_speed", 80.0)
        self.hit_duration = float = stats.get("hit_duration", 0.35)
        self.death_duration = float = stats.get("death_duration",1.0)

        # AI config
        ai = defn["ai"]
        self.walk_speed: float     = ai["walk_speed"]
        self.patrol_dist: float    = ai["patrol_dist"]
        self.detect_range: float   = ai["detect_range"]
        self.attack_range: float   = ai["attack_range"]
        self.attack_reach: float   = ai.get("attack_reach", 28.0)
        self.attack_timing: tuple  = ai.get("attack_timing", (0.45, 0.60))
        self.attack_duration: float = ai.get("attack_duration", 0.8)
        self.attack_cooldown: float = ai.get("attack_cooldown", 1.5)
        self.float_amplitude: float = ai.get("float_amplitude", 0.0)
        self.float_speed: float    = ai.get("float_speed", 0.0)
        self.can_jump: bool        = ai.get("can_jump", False)
        self.jump_velocity: float  = ai.get("jump_velocity", -240.0)

        # Patrol bookkeeping
        self.spawn_x: float = x
        self.spawn_y: float = y
        self.float_timer: float = 0.0   # for monster_eyes oscillation

        self.hit_flash_timer: float = 0.0
        self.room: Any = None
        self.player: Any = None

        # Build animations using base Entity helper
        enemy_anims = defn.get("animations", {})
        frame_rects = settings.FRAMES[enemy_type]
        self.animations: Dict[str, Animation] = self._create_animations(enemy_anims, frame_rects)
        self.current_animation: Optional[Animation] = self.animations.get("idle")

        # Auto-enable jump capability if entity has a jump animation defined
        if "jump" in self.animations:
            self.can_jump = True

        self.state_machine = StateMachine({
            "patrol": lambda sm: EnemyPatrolState(self, sm),
            "chase":  lambda sm: EnemyChaseState(self, sm),
            "attack": lambda sm: EnemyAttackState(self, sm),
            "hit":    lambda sm: EnemyHitState(self, sm),
            "death":  lambda sm: EnemyDeathState(self, sm),
        })
        self.change_state("patrol")

        self.player: Optional["Player"] = None
        self.hazards: list[dict] = []
        self.projectiles: list[dict] = []
        self.cultist_corruptions: list[dict] = []
        self.on_hazard_hit: Optional[Any] = None
        self.dead: bool = False
        self.in_arena: bool = False

    def spawn_projectile(self, speed: float = 160.0, damage: int = 12) -> None:
        direction = 1.0 if self.facing == "right" else -1.0
        spawn_x = float(self.hitbox.right + 6 if direction > 0 else self.hitbox.left - 6)
        spawn_y = float(self.hitbox.centery - 2.0)
        col = (255, 220, 70) if self.phase == "green" else (255, 80, 80)
        if hasattr(self, "room") and self.room is not None:
            self.room.spawn_enemy_projectile(spawn_x, spawn_y, speed * direction, damage, col)
        else:
            self.projectiles.append({
                "x": spawn_x,
                "y": spawn_y,
                "vx": speed * direction,
                "damage": damage,
                "life": 2.5,
                "color": col,
                "trail": [],
            })

    def spawn_cultist_corruption(self, tx: float, base_y: float, delay: float = 0.0, damage: int = 14) -> None:
        self.cultist_corruptions.append({
            "x": tx,
            "base_y": base_y,
            "timer": -delay,
            "duration": 0.65,
            "damage": damage,
            "hitbox": pygame.Rect(int(tx - 12), int(base_y - 36), 24, 36),
            "resolved": False,
            "particles": [],
        })

    def is_active(self) -> bool:
        if self.phase == "neutral" or self.in_arena:
            return True
        if self.player is None:
            return True
        return self.player.phase_color == self.phase

    def distance_to_player(self) -> float:
        if self.player is None:
            return float("inf")
        dx = self.hitbox.centerx - self.player.hitbox.centerx
        dy = self.hitbox.centery - self.player.hitbox.centery
        return math.hypot(dx, dy)

    def horizontal_distance_to_player(self) -> float:
        if self.player is None:
            return float("inf")
        return abs(self.hitbox.centerx - self.player.hitbox.centerx)

    def vertical_distance_to_player(self) -> float:
        if self.player is None:
            return 0.0
        return self.player.hitbox.centery - self.hitbox.centery

    def player_direction(self) -> int:
        if self.player is None:
            return 1
        return 1 if self.player.hitbox.centerx >= self.hitbox.centerx else -1

    def get_action(self, action_name: str) -> dict:
        actions = self.defn.get("actions", {})
        if action_name in actions:
            return actions[action_name]
        return {
            "name": action_name,
            "damage": self.contact_damage,
            "reach": self.attack_reach,
            "timing": self.attack_timing,
            "duration": self.attack_duration,
            "func": entity_defs.enemy_melee_attack,
        }

    def take_damage(self, amount: float) -> None:
        if not self.is_active():
            return
        if self.state_name == "death":
            return
        self._health = max(0.0, self._health - amount)
        self.hit_flash_timer = 0.25
        if self._health <= 0.0:
            self.change_state("death")
        else:
            self.change_state("hit")

    def update(self, dt: float) -> None:
        if self.hit_flash_timer > 0.0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

        if self.float_amplitude > 0:
            self.float_timer += dt

        # Actualizar proyectiles / balas
        for p in self.projectiles[:]:
            p["life"] -= dt
            p["x"] += p["vx"] * dt
            p["trail"].append({"x": p["x"], "y": p["y"], "life": 0.12})
            for tr in p["trail"][:]:
                tr["life"] -= dt
                if tr["life"] <= 0:
                    p["trail"].remove(tr)

            # Colisión con el jugador
            player = self.player
            if player is not None and not player.is_dead() and self.is_active():
                p_rect = pygame.Rect(int(p["x"] - 5), int(p["y"] - 3), 10, 6)
                is_sword_special = (player.state_name == "attack_special" and player.skin == "sword")
                if (
                    player.state_name not in ("hit", "death", "dash")
                    and not is_sword_special
                    and player.invulnerable_timer <= 0.0
                    and p_rect.colliderect(player.hitbox)
                ):
                    player.take_damage(int(p["damage"]), source_x=p["x"])
                    if self.on_hazard_hit:
                        self.on_hazard_hit({"damage": p["damage"], "hitbox": p_rect})
                    if p in self.projectiles:
                        self.projectiles.remove(p)
                    continue

            # Despawn al salir del mapa o impactar los bordes de la sala
            if p["x"] <= 16.0 or p["x"] >= float(settings.VIRTUAL_WIDTH if not hasattr(self, "map_w") else self.map_w) - 16.0:
                if p in self.projectiles:
                    self.projectiles.remove(p)
                continue

            if p["life"] <= 0 and p in self.projectiles:
                self.projectiles.remove(p)

        # Actualizar raíces del jefe
        for h in list(self.hazards):
            h["timer"] += dt
            if h["timer"] < 0.0:
                continue
            if not h.get("resolved", False) and h["timer"] >= 0.80:
                h["resolved"] = True
                p = self.player
                is_sword_special = (p is not None and p.state_name == "attack_special" and p.skin == "sword")
                if (
                    self.is_active()
                    and p is not None
                    and not p.is_dead()
                    and p.state_name not in ("hit", "death", "dash")
                    and not is_sword_special
                    and p.invulnerable_timer <= 0.0
                    and h["hitbox"].colliderect(p.hitbox)
                ):
                    h["hit"] = True
                    p.take_damage(int(h["damage"]), source_x=h["hitbox"].centerx)
                    if self.on_hazard_hit:
                        self.on_hazard_hit(h)
                else:
                    h["hit"] = False
                    h["miss"] = True
        self.hazards = [h for h in self.hazards if h["timer"] < h["duration"]]

        if not self.is_active():
            # Ghost mode: tick animation but freeze AI
            self._tick_anim(dt)
            return

        super().update(dt)

    def render(
        self,
        surface: pygame.Surface,
        camera_x: float = 0.0,
        camera_y: float = 0.0,
    ) -> None:
        # Renderizar raíces del jefe (big_monster vines)
        for h in self.hazards:
            if h["timer"] < 0.0:
                continue
            frame_idx = min(15, int(h["timer"] / h["interval"]))
            v_frames = settings.FRAMES.get("boss_vines", {})
            if h.get("miss"):
                f_list = v_frames.get("miss", [])
            else:
                f_list = v_frames.get(h.get("variant", "2c"), v_frames.get("2c", []))

            if f_list and frame_idx < len(f_list):
                h_surf = f_list[frame_idx]
                hx = int(h["x"] - camera_x)
                hy = int(h["y"] - camera_y)
                if self.is_active():
                    self.render_outline(surface, h_surf, hx, hy, (255, 90, 90, 180))
                    surface.blit(h_surf, (hx, hy))
                else:
                    ghost = self._ghost_cache.get(id(h_surf))
                    if ghost is None:
                        ghost = pygame.Surface(h_surf.get_size(), pygame.SRCALPHA)
                        ghost.blit(h_surf, (0, 0))
                        ghost.fill((255, 255, 255, self.GHOST_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
                        self._ghost_cache[id(h_surf)] = ghost
                    surface.blit(ghost, (hx, hy))

        # Renderizar proyectiles / balas
        if self.projectiles:
            if Enemy._plasma_bullet_surf is None:
                Enemy._plasma_trail_surf = pygame.Surface((6, 4), pygame.SRCALPHA)
                b_surf = pygame.Surface((10, 6), pygame.SRCALPHA)
                b_surf.fill((0, 0, 0, 0))
                pygame.draw.ellipse(b_surf, (255, 90, 40, 200), (0, 0, 10, 6))
                pygame.draw.ellipse(b_surf, (255, 245, 160, 255), (2, 1, 6, 4))
                Enemy._plasma_bullet_surf = b_surf

            for p in self.projectiles:
                px = int(p["x"] - camera_x)
                py = int(p["y"] - camera_y)
                # Rastro
                for tr in p.get("trail", []):
                    tx = int(tr["x"] - camera_x)
                    ty = int(tr["y"] - camera_y)
                    tr_alpha = int(180 * (tr["life"] / 0.12))
                    if Enemy._plasma_trail_surf:
                        Enemy._plasma_trail_surf.fill((0, 0, 0, 0))
                        pygame.draw.ellipse(Enemy._plasma_trail_surf, (255, 120, 40, tr_alpha), (0, 0, 6, 4))
                        surface.blit(Enemy._plasma_trail_surf, (tx - 3, ty - 2))

                # Núcleo de plasma
                if Enemy._plasma_bullet_surf:
                    surface.blit(Enemy._plasma_bullet_surf, (px - 5, py - 3))

        frame = self.current_animation.get_current_frame()
        draw_x = self.hitbox.x + self.render_offset_x - camera_x
        draw_y = self.hitbox.y + self.render_offset_y - camera_y

        if isinstance(frame, pygame.Surface):
            sub = frame
        else:
            sub = settings.TEXTURES[self.enemy_type].subsurface(frame)

        default_facing = self.defn.get("default_facing", "right")
        needs_flip = (self.facing != default_facing)
        if needs_flip:
            sub_id = id(sub)
            sprite_surf = self._flip_cache.get(sub_id)
            if sprite_surf is None:
                sprite_surf = pygame.transform.flip(sub, True, False)
                self._flip_cache[sub_id] = sprite_surf
        else:
            sprite_surf = sub

        if self.is_active():
            outline_col = (255, 90, 90, 200) if self.phase == "red" else (90, 240, 150, 200)
            self.render_outline(surface, sprite_surf, draw_x, draw_y, outline_col)
            surface.blit(sprite_surf, (draw_x, draw_y))
        else:
            ghost = self._ghost_cache.get(id(sprite_surf))
            if ghost is None:
                ghost = pygame.Surface(sprite_surf.get_size(), pygame.SRCALPHA)
                ghost.blit(sprite_surf, (0, 0))
                ghost.fill((255, 255, 255, self.GHOST_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
                self._ghost_cache[id(sprite_surf)] = ghost
            surface.blit(ghost, (draw_x, draw_y))
