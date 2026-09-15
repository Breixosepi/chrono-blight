import pygame
import random
from typing import Any, Optional

import settings
from src.definitions import entity as entity_defs
from src.world.tile_collision import collision_type_in_layers
from gale.tilemap.collision import CollisionType

class FallingTrap:
    def __init__(
        self,
        room: Any,
        x: float,
        y: float,
        phase: str,
        tile_col: int = 1,
        tile_row: int = 2,
        width: int = 16,
        height: int = 16,
    ):
        self.room = room
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.hitbox = pygame.Rect(int(x), int(y), self.width, self.height)
        self.phase = phase
        
        self.state = "hidden"
        self.shake_timer = 0.0
        self.vy = 0.0
        self.damage = 20
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.frames = settings.FRAMES.get("destructible_block", [])
        self.texture = settings.TEXTURES.get("destructible_block")
        self.frame_index = 0
        self.anim_timer = 0.0
        self.frame_time = 0.06 # Fast animation for shaking/breaking
        
        # We will use frames[0] as idle, frames[1..3] for shaking, frames[4..6] for breaking
        if self.frames and self.texture:
            self.image = self.texture.subsurface(self.frames[0])
        else:
            self.image.fill((80, 220, 100) if phase == "green" else (220, 60, 60))
            
        self.shaking_offset_x = 0.0
        self.shaking_offset_y = 0.0

    def reset(self) -> None:
        self.x = self.start_x
        self.y = self.start_y
        self.hitbox.x = int(self.x)
        self.hitbox.y = int(self.y)
        self.vy = 0.0
        self.state = "hidden"
        self.frame_index = 0
        self.anim_timer = 0.0
        self.shaking_offset_x = 0.0
        self.shaking_offset_y = 0.0
        if self.frames and self.texture:
            self.image = self.texture.subsurface(self.frames[0])

    def break_trap(self) -> None:
        self.state = "broken"
        self.room.spawn_dust(self.hitbox.centerx, self.hitbox.bottom, count=5)

    def update(self, dt: float) -> None:
        # Resets if the player leaves the trap's phase, meaning if they switch back it will fall again.
        if self.room.player.phase_color != self.phase:
            if self.state != "hidden":
                self.reset()
            return
            
        # Active phase logic
        if self.state == "hidden":
            self.state = "idle"
            if self.frames and self.texture:
                self.image = self.texture.subsurface(self.frames[0])
            
        # Animation logic for breaking state
        if self.state == "broken" and self.frames and self.texture:
            self.anim_timer += dt
            if self.anim_timer >= self.frame_time:
                self.anim_timer = 0.0
                if self.frame_index < 1:
                    self.frame_index = 1
                elif self.frame_index < 7:
                    self.frame_index += 1
                self.image = self.texture.subsurface(self.frames[self.frame_index])

        if self.state == "idle":
            # Revisa la distancia en el eje X
            dist_x = abs(self.hitbox.centerx - self.room.player.hitbox.centerx)
            # Revisa que el jugador esté debajo de la trampa
            if dist_x < 48 and self.room.player.hitbox.centery > self.hitbox.centery:
                self.state = "shaking"
                self.shake_timer = 0.45  # Short warning before dropping
        elif self.state == "shaking":
            self.shake_timer -= dt
            if self.shake_timer > 0:
                self.shaking_offset_x = random.uniform(-2, 2)
                self.shaking_offset_y = random.uniform(-1, 1)
            else:
                self.state = "falling"
                self.shaking_offset_x = 0.0
                self.shaking_offset_y = 0.0
                self.vy = 0.0
        elif self.state == "falling":
            self.vy += entity_defs.GRAVITY * dt
            self.y += self.vy * dt
            self.hitbox.y = int(self.y)
            
            player = self.room.player
            if not player.is_dead() and self.hitbox.colliderect(player.hitbox):
                if player.invulnerable_timer <= 0:
                    player.take_damage(self.damage)
                    self.room.camera.shake(3.0, 0.2)
                    self.room._spawn_popup(f"-{self.damage} (TRAP)", player.hitbox.centerx, player.hitbox.top - 10, 0.7, (255, 60, 60))
                self.break_trap()
                return
                
            # Solo revisamos colisión con el mapa después de que ha bajado al menos 16 píxeles
            # para evitar que colisione instantáneamente con la plataforma en la que está anclada
            if self.y > self.start_y + 16:
                row = self.hitbox.bottom // 16
                col1 = self.hitbox.left // 16
                col2 = self.hitbox.right // 16
                layers = self.room._get_active_collision_layers()
                
                t1 = collision_type_in_layers(self.room.tilemap, layers, row, col1)
                t2 = collision_type_in_layers(self.room.tilemap, layers, row, col2)
                
                if t1 == CollisionType.SOLID or t2 == CollisionType.SOLID or self.y > self.room.MAP_HEIGHT:
                    self.break_trap()

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        if self.state == "hidden" or self.room.player.phase_color != self.phase:
            return
            
        if self.state == "broken" and getattr(self, "frame_index", 0) >= 7:
            # Full break animation finished, don't draw
            return
            
        draw_x = self.x - camera_x + self.shaking_offset_x
        draw_y = self.y - camera_y + self.shaking_offset_y
        
        surface.blit(self.image, (draw_x, draw_y))

