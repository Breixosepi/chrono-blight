"""
Chrono Blight - Collectible Health Drop (HealthOrb)
"""
import random
from typing import Any, List, Optional
import pygame
from gale.animation import Animation

import settings
from src.entities.Player import Player
from src.world.tile_collision import move_and_collide_layers


class HealthOrb:
    _FRAMES: Optional[List[pygame.Surface]] = None

    def __init__(self, x: float, y: float, room: Any) -> None:
        self.x = x
        self.y = y
        self.vx = random.uniform(-40.0, 40.0)
        self.vy = random.uniform(-100.0, -150.0)
        self.room = room
        self.width = 12
        self.height = 12

        self._init_shared_frames()
        self.animation = Animation(self._FRAMES, 0.10)

        self.hitbox = pygame.Rect(int(x + 2), int(y + 2), 8, 8)
        self.is_dead = False
        self.heal_amount = 20

    @classmethod
    def _init_shared_frames(cls) -> None:
        if cls._FRAMES is None:
            tex = settings.TEXTURES["animated_items"]
            cls._FRAMES = [
                pygame.transform.scale(tex.subsurface(pygame.Rect(i * 32, 32, 32, 32)), (12, 12))
                for i in range(6)
            ]

    def update(self, dt: float, player: Player) -> None:
        if self.is_dead:
            return

        self.vy += 400.0 * dt
        dx = self.vx * dt
        dy = self.vy * dt

        collision_layers = player.active_collision_layers

        new_x, new_y, collided_x, collided_y = move_and_collide_layers(
            self.room.tilemap,
            collision_layers,
            self.x + 2,
            self.y + 2,
            12,
            12,
            dx,
            dy,
        )

        max_x = float(self.room.MAP_WIDTH - self.width)
        self.x = max(0.0, min(max_x, new_x - 2))
        self.y = new_y - 2
        self.hitbox.topleft = (int(self.x + 2), int(new_y))

        if collided_x or self.x <= 0.0 or self.x >= max_x:
            self.vx = -self.vx * 0.5

        if collided_y:
            if self.vy > 0:
                self.vy = -self.vy * 0.3
                if abs(self.vy) < 20.0:
                    self.vy = 0.0
                    self.vx = 0.0
            else:
                self.vy = 0.0

        self.animation.update(dt)

        if self.hitbox.colliderect(player.hitbox):
            if player.health < player.MAX_HEALTH:
                player.health = min(player.MAX_HEALTH, player.health + self.heal_amount)
                settings.SOUNDS["heart"].play()
                self.room._spawn_popup(
                    f"+{self.heal_amount}",
                    self.hitbox.centerx,
                    self.hitbox.top - 8,
                    0.7,
                    (100, 255, 100),
                )
                self.is_dead = True

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        if self.is_dead:
            return
        frame = self.animation.get_current_frame()
        surface.blit(frame, (int(self.x - camera_x), int(self.y - camera_y)))