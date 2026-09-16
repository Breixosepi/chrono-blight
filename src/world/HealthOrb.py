"""
Chrono Blight - Collectible Health Drop (HealthOrb)
"""
import random
from typing import Any
import pygame

import settings
from src.entities.Player import Player
from src.world.tile_collision import move_and_collide_layers


class HealthOrb:
    def __init__(self, x: float, y: float, room: Any):
        self.x = x
        self.y = y
        self.vx = random.uniform(-40.0, 40.0)
        self.vy = random.uniform(-100.0, -150.0)
        self.room = room

        # Scale down heart from 32x32 to 16x16 for crisp pixel pickup size
        self.width = 16
        self.height = 16
        tex = settings.TEXTURES["animated_items"]
        raw_frames = [tex.subsurface(pygame.Rect(i * 32, 32, 32, 32)) for i in range(6)]
        self.frames = [pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames]
        self.frame_index = 0.0

        # Hitbox (centered 12x12)
        self.hitbox = pygame.Rect(int(x + 2), int(y + 2), 12, 12)

        self.is_dead = False
        self.heal_amount = 20

    def update(self, dt: float, player: Player) -> None:
        if self.is_dead:
            return

        # Physics & gentle gravity
        self.vy += 400.0 * dt
        dx = self.vx * dt
        dy = self.vy * dt

        collision_layers = [f"{self.room.player.phase_color}_ground", "ground"]

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

        self.x = new_x - 2
        self.y = new_y - 2
        self.hitbox.x = int(new_x)
        self.hitbox.y = int(new_y)

        if collided_x:
            self.vx = -self.vx * 0.5

        if collided_y:
            if self.vy > 0:
                self.vy = -self.vy * 0.3
                if abs(self.vy) < 20:
                    self.vy = 0
                    self.vx = 0
            else:
                self.vy = 0

        # Animation
        self.frame_index += 10.0 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0.0

        # Collect upon collision with player
        if self.hitbox.colliderect(player.hitbox):
            if player.health < player.MAX_HEALTH:
                player.health = min(player.MAX_HEALTH, player.health + self.heal_amount)
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
        frame = self.frames[int(self.frame_index)]
        surface.blit(frame, (int(self.x - camera_x), int(self.y - camera_y)))

