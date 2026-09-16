"""
Chrono Blight - Saw/Shuriken Hazard
"""
import pygame
from typing import Any
from gale.animation import Animation
import settings


class SawHazard:
    def __init__(
        self,
        room: Any,
        x: float,
        y: float,
        hazard_type: str = "saw",
        phase: str = "neutral",
        patrol_dist: float = 0.0,
        axis: str = "y",
        speed: float = 50.0,
        damage: int = 15,
    ):
        self.room = room
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        
        hitbox_size = 24
        self.hitbox_offset = (32 - hitbox_size) // 2
        self.hitbox = pygame.Rect(
            int(x) + self.hitbox_offset, 
            int(y) + self.hitbox_offset, 
            hitbox_size, 
            hitbox_size
        )
        
        self.hazard_type = hazard_type
        self.phase = phase
        self.patrol_dist = patrol_dist
        self.axis = axis.lower()
        self.speed = speed
        self.damage = damage
        self.direction = 1
        
        tex_key = "saw_blade" if self.hazard_type in ("saw", "shuriken") else self.hazard_type
        tex = settings.TEXTURES.get(tex_key)
        rects = settings.FRAMES.get(tex_key, [])
        
        if tex and rects:
            surfaces = [tex.subsurface(r) for r in rects]
            self.animation = Animation(surfaces, 0.08)
        else:
            self.animation = None
            
        self.fallback_image = pygame.Surface((self.width, self.height))
        self.fallback_image.fill((150, 150, 150))

    def update(self, dt: float) -> None:
        if self.phase != "neutral" and self.room.player.phase_color != self.phase:
            return
            
        if self.animation:
            self.animation.update(dt)

        if self.patrol_dist > 0:
            if self.axis == "y":
                self.y += self.direction * self.speed * dt
                if self.direction > 0 and self.y >= self.start_y + self.patrol_dist:
                    self.y = self.start_y + self.patrol_dist
                    self.direction = -1
                elif self.direction < 0 and self.y <= self.start_y:
                    self.y = self.start_y
                    self.direction = 1
            else:
                self.x += self.direction * self.speed * dt
                if self.direction > 0 and self.x >= self.start_x + self.patrol_dist:
                    self.x = self.start_x + self.patrol_dist
                    self.direction = -1
                elif self.direction < 0 and self.x <= self.start_x:
                    self.x = self.start_x
                    self.direction = 1
                    
        self.hitbox.topleft = (int(self.x) + self.hitbox_offset, int(self.y) + self.hitbox_offset)

        player = self.room.player
        if not player.is_dead() and self.hitbox.colliderect(player.hitbox):
            if player.invulnerable_timer <= 0:
                player.take_damage(self.damage)
                self.room.camera.shake(3.0, 0.2)
                self.room._spawn_popup(
                    f"-{self.damage}",
                    player.hitbox.centerx,
                    player.hitbox.top - 10,
                    0.7,
                    (255, 60, 60),
                )

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        if self.phase != "neutral" and self.room.player.phase_color != self.phase:
            return
            
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        if self.animation:
            frame_surf = self.animation.get_current_frame()
            surface.blit(frame_surf, (draw_x, draw_y))
        else:
            surface.blit(self.fallback_image, (draw_x, draw_y))