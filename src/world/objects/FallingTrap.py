import random
from typing import Any
import pygame
from gale.animation import Animation
from gale.timer import Timer
from gale.tilemap.collision import CollisionType

import settings
from src.definitions import entity as entity_defs
from src.world.systems.tile_collision import collision_type_in_layers


class FallingTrap:
    def __init__(
        self,
        room: Any,
        x: float,
        y: float,
        phase: str,
        width: int = 32,   
        height: int = 32,
        damage: int = 20,  
    ):
        self.room = room
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(int(x), int(y), self.width, self.height)
        self.phase = phase
        self.damage = damage
        
        self.state = "hidden"
        self.vy = 0.0
        
        self.texture = settings.TEXTURES.get("destructible_block")
        frames = settings.FRAMES.get("destructible_block", [])
        
        self.idle_frame = frames[0] if frames else None
        break_frames = frames[1:7] if frames else []
        self.break_animation = Animation(break_frames, 0.06, loops=1)
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._set_idle_image()
            
        self.shaking_offset_x = 0.0
        self.shaking_offset_y = 0.0

    def _set_idle_image(self) -> None:
        if self.idle_frame and self.texture:
            self.image = self.texture.subsurface(self.idle_frame)
        else:
            self.image.fill((80, 220, 100) if self.phase == "green" else (220, 60, 60))

    def reset(self) -> None:
        self.x = self.start_x
        self.y = self.start_y
        self.hitbox.x = int(self.x)
        self.hitbox.y = int(self.y)
        self.vy = 0.0
        self.state = "hidden"
        self.shaking_offset_x = 0.0
        self.shaking_offset_y = 0.0
        
        self.break_animation.reset()
        self._set_idle_image()

    def break_trap(self) -> None:
        self.state = "broken"
        settings.SOUNDS["rock-smash"].play()
        self.room.spawn_dust(self.hitbox.centerx, self.hitbox.bottom, count=5)
        self.break_animation.reset()

    def _start_falling(self) -> None:
        if self.state == "shaking":
            self.state = "falling"
            self.shaking_offset_x = 0.0
            self.shaking_offset_y = 0.0
            self.vy = 0.0

    def update(self, dt: float) -> None:
        if self.room.player.phase_color != self.phase:
            if self.state != "hidden":
                self.reset()
            return
            
        if self.state == "hidden":
            self.state = "idle"
            self._set_idle_image()
                
        if self.state == "broken" and self.texture:
            self.break_animation.update(dt)
            if self.break_animation.times_played == 0:
                self.image = self.texture.subsurface(self.break_animation.get_current_frame())

        if self.state == "idle":
            dist_x = abs(self.hitbox.centerx - self.room.player.hitbox.centerx)
            if dist_x < 48 and self.room.player.hitbox.centery > self.hitbox.centery:
                self.state = "shaking"
                settings.SOUNDS["rock-crack"].play()
                Timer.after(0.45, self._start_falling)
                
        elif self.state == "shaking":
            self.shaking_offset_x = random.uniform(-2, 2)
            self.shaking_offset_y = random.uniform(-1, 1)
            
        elif self.state == "falling":
            self.vy += entity_defs.GRAVITY * dt
            self.y += self.vy * dt
            self.hitbox.y = int(self.y)
            
            player = self.room.player
            if not player.is_dead() and self.hitbox.colliderect(player.hitbox):
                if player.invulnerable_timer <= 0:
                    player.take_damage(self.damage)
                    self.room.camera.shake(3.0, 0.2)
                    self.room._spawn_popup(f"-{self.damage}", player.hitbox.centerx, player.hitbox.top - 10, 0.7, (255, 60, 60))
                self.break_trap()
                return
                
            tile_size = getattr(self.room, "TILE_SIZE", 16)
            if self.y > self.start_y + tile_size:
                row = self.hitbox.bottom // tile_size
                col1 = self.hitbox.left // tile_size
                col2 = self.hitbox.right // tile_size
                layers = self.room._get_active_collision_layers()
                
                t1 = collision_type_in_layers(self.room.tilemap, layers, row, col1)
                t2 = collision_type_in_layers(self.room.tilemap, layers, row, col2)
                
                if t1 == CollisionType.SOLID or t2 == CollisionType.SOLID or self.y > self.room.MAP_HEIGHT:
                    self.break_trap()

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        if self.state == "hidden" or self.room.player.phase_color != self.phase:
            return
            
        if self.state == "broken" and self.break_animation.times_played > 0:
            return
            
        draw_x = self.x - camera_x + self.shaking_offset_x
        draw_y = self.y - camera_y + self.shaking_offset_y
        
        surface.blit(self.image, (draw_x, draw_y))