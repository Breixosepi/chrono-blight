"""
Chrono Blight
"""

from typing import Any, Optional, Dict, Tuple
import pygame
from gale.animation import Animation
from gale.state import StateMachine

import settings
from src.definitions import entity as entity_defs


class Entity:

    def __init__(
        self,
        x: float,
        y: float,
        width: int = entity_defs.PLAYER_HIT_W,
        height: int = entity_defs.PLAYER_HIT_H,
        floor_y: float = 160.0,
        map_w: float = 1248.0,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height
        self.floor_y: float = floor_y
        self.map_w: float = map_w

        self.hitbox: pygame.Rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height,
        )

        self.vx: float = 0.0
        self.vy: float = 0.0
        self.on_ground: bool = False
        self.facing: str = "right"

        self.move_direction: int = 0
        self.jump_requested: bool = False
        self.jump_held: bool = False
        self.is_looking_up: bool = False
        self.is_running: bool = False
        self.attack_requested: bool = False
        self.special_attack_requested: bool = False
        self.dash_requested: bool = False

        self.state_machine: Optional[StateMachine] = None
        self.state_name: str = ""

        self.animations: Dict[str, Any] = {}
        self.current_animation: Optional[Animation] = None
        self._anim_timer: float = 0.0
        self._last_anim_name: str = "idle"

        self.invulnerable_timer: float = 0.0
        self.hit_flash_timer: float = 0.0

        self._health: float = 100.0
        self._max_health: float = 100.0

    @staticmethod
    def _create_animations(
        animation_defs: Dict[str, Dict[str, Any]],
        frame_source: Any,
    ) -> Dict[str, Animation]:
        animations: Dict[str, Animation] = {}
        for name, anim_data in animation_defs.items():
            rects = [frame_source[i] for i in anim_data["frames"]]
            animations[name] = Animation(
                rects,
                anim_data["interval"],
                loops=anim_data.get("loops"),
            )
        return animations

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, val: float) -> None:
        self._health = val

    @property
    def MAX_HEALTH(self) -> float:
        return self._max_health

    def change_state(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.state_name = name
        if self.state_machine is not None:
            self.state_machine.change(name, *args, **kwargs)

    def is_busy(self) -> bool:
        return self.state_name in {"attack", "attack_special", "dash", "hit", "death"}

    def change_animation(self, new_anim_name: str) -> None:
        if new_anim_name == self._last_anim_name and self.current_animation is not None:
            return
        self._last_anim_name = new_anim_name
        self._anim_timer = 0.0
        if isinstance(self.animations, dict) and new_anim_name in self.animations:
            self.current_animation = self.animations[new_anim_name]
            if self.current_animation is not None:
                self.current_animation.reset()

    def _tick_anim(self, dt: float) -> None:
        self._anim_timer += dt
        if self.current_animation:
            self.current_animation.update(dt)

    def is_animation_finished(self, fallback_duration: Optional[float] = None) -> bool:
        if self.current_animation is not None and self.current_animation.times_played > 0:
            return True
        if fallback_duration is None and self.current_animation is not None:
            fallback_duration = self.current_animation.size * self.current_animation.interval
        if fallback_duration is not None and self._anim_timer >= fallback_duration:
            return True
        return False

    def collides(self, target: Any) -> bool:
        target_rect = getattr(target, "hitbox", getattr(target, "rect", None))
        if target_rect is not None:
            return self.hitbox.colliderect(target_rect)
        if hasattr(target, "x") and hasattr(target, "y") and hasattr(target, "width") and hasattr(target, "height"):
            target_rect = pygame.Rect(round(target.x), round(target.y), target.width, target.height)
            return self.hitbox.colliderect(target_rect)
        return False

    def _apply_movement_and_collision(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.hitbox.x = int(self.x)
        self.hitbox.y = int(self.y)

        if self.hitbox.left < 0:
            self.hitbox.left = 0
            self.x = float(self.hitbox.x)
            self.vx = 0.0
        elif self.hitbox.right > int(self.map_w):
            self.hitbox.right = int(self.map_w)
            self.x = float(self.hitbox.x)
            self.vx = 0.0

        if self.hitbox.bottom >= int(self.floor_y):
            self.hitbox.bottom = int(self.floor_y)
            self.y = float(self.hitbox.y)
            self.vy = 0.0
            if not self.on_ground:
                self.on_ground = True
                self.on_land()
        else:
            self.on_ground = False

    def on_land(self) -> None:
        current_state = self.state_machine.current if self.state_machine else None
        if hasattr(current_state, "on_land"):
            current_state.on_land()

    def update(self, dt: float) -> None:
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
        if self.hit_flash_timer > 0.0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

        current_state = self.state_machine.current if self.state_machine else None

        if getattr(current_state, "has_gravity", True):
            self.vy += entity_defs.GRAVITY * dt

        if self.state_machine is not None:
            self.state_machine.update(dt)

        self._tick_anim(dt)
        self._apply_movement_and_collision(dt)

    def take_damage(self, amount: int) -> None:
        if self.state_name in {"hit", "death"}:
            return
        self.health = max(0.0, self.health - amount)
        if self.health == 0.0:
            self.change_state("death")
        else:
            self.change_state("hit")

    def is_dead(self) -> bool:
        return self.health <= 0.0

    @staticmethod
    def render_outline(
        surface: pygame.Surface,
        sprite_surf: pygame.Surface,
        draw_x: float,
        draw_y: float,
        outline_color: Tuple[int, int, int, int],
    ) -> None:
        mask = pygame.mask.from_surface(sprite_surf)
        outline_surf = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            surface.blit(outline_surf, (draw_x + dx, draw_y + dy))

    def render(
        self,
        surface: pygame.Surface,
        camera_x: float = 0.0,
        camera_y: float = 0.0,
    ) -> None:
        pass
