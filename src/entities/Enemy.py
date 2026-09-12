import math
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

    GHOST_ALPHA: int = 85

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
        self.on_hazard_hit: Optional[Any] = None
        self.dead: bool = False


    def is_active(self) -> bool:
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

        for h in list(self.hazards):
            h["timer"] += dt
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
        for h in self.hazards:
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
                    ghost = h_surf.copy()
                    ghost.set_alpha(65)
                    surface.blit(ghost, (hx, hy))

        frame = self.current_animation.get_current_frame()
        draw_x = self.hitbox.x + self.render_offset_x - camera_x
        draw_y = self.hitbox.y + self.render_offset_y - camera_y

        if isinstance(frame, pygame.Surface):
            sub = frame
        else:
            sub = settings.TEXTURES[self.enemy_type].subsurface(frame)

        default_facing = entity_defs.ENEMY_DEFS[self.enemy_type].get("default_facing", "right")
        needs_flip = (self.facing != default_facing)
        if needs_flip:
            sprite_surf = pygame.transform.flip(sub, True, False)
        else:
            sprite_surf = sub

        if self.is_active():
            outline_col = (255, 90, 90, 200) if self.phase == "red" else (90, 240, 150, 200)
            self.render_outline(surface, sprite_surf, draw_x, draw_y, outline_col)
            surface.blit(sprite_surf, (draw_x, draw_y))

        else:
            ghost = sprite_surf.copy()
            ghost.set_alpha(65)
            surface.blit(ghost, (draw_x, draw_y))

