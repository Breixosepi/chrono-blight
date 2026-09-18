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
        initial_direction: int = 1,
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
        self.direction = initial_direction
        self.initial_direction = initial_direction

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
        self.stopped: bool = False

    def stop(self) -> None:
        self.stopped = True
        self.speed = 0.0

    def update(self, dt: float) -> None:
        if self.stopped:
            return
        if self.phase != "neutral" and self.room.player.phase_color != self.phase:
            return
            
        if self.animation:
            self.animation.update(dt)

        if self.patrol_dist > 0:
            if self.axis == "y":
                min_y = self.start_y if self.initial_direction == 1 else self.start_y - self.patrol_dist
                max_y = self.start_y + self.patrol_dist if self.initial_direction == 1 else self.start_y
                self.y += self.direction * self.speed * dt
                if self.direction > 0 and self.y >= max_y:
                    self.y = max_y
                    self.direction = -1
                elif self.direction < 0 and self.y <= min_y:
                    self.y = min_y
                    self.direction = 1
            else:
                min_x = self.start_x if self.initial_direction == 1 else self.start_x - self.patrol_dist
                max_x = self.start_x + self.patrol_dist if self.initial_direction == 1 else self.start_x
                self.x += self.direction * self.speed * dt
                if self.direction > 0 and self.x >= max_x:
                    self.x = max_x
                    self.direction = -1
                elif self.direction < 0 and self.x <= min_x:
                    self.x = min_x
                    self.direction = 1
                    
        self.hitbox.topleft = (int(self.x) + self.hitbox_offset, int(self.y) + self.hitbox_offset)

        player = self.room.player
        if not player.is_dead() and self.hitbox.colliderect(player.hitbox):
            if player.state_name != "dash" and player.invulnerable_timer <= 0:
                settings.SOUNDS["saw-hazard"].play()
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