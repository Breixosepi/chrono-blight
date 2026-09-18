"""
Chrono Blight - LightMonolith
Interactive monoliths that illuminate the arena and stun The Harvester in Phase 2.
"""
from typing import Optional, List, Tuple
import math
import pygame
from gale.animation import Animation

import settings


class LightMonolith:
    def __init__(self, x: float, y: float, phase: str = "green", on_activated=None) -> None:
        self.x: float = x
        self.y: float = y
        self.phase: str = phase
        self.on_activated = on_activated

        self.width: int = 54
        self.height: int = 169
        self.hitbox: pygame.Rect = pygame.Rect(int(x + 7), int(y + 60), 40, 105)

        self.is_activated: bool = False
        self.pulse_timer: float = 0.0

        self._frames: List[pygame.Surface] = settings.FRAMES.get("monolith_frames", [])
        self.glow_color: Tuple[int, int, int] = (90, 240, 150) if phase == "green" else (255, 90, 90)

        self.animation = Animation(
            self._frames if self._frames else [pygame.Surface((self.width, self.height))],
            0.045,
            loops=1
        )

    def update(self, dt: float) -> None:
        self.pulse_timer += dt * 3.5
        
        if self.is_activated:
            self.animation.update(dt)

    def reset(self) -> None:
        self.is_activated = False
        self.animation.reset()
        self.pulse_timer = 0.0

    def take_hit(self, player_phase: str, room=None) -> bool:
        if self.is_activated:
            return False

        if player_phase != self.phase:
            if room:
                room.camera.shake(1.5, 0.1)
                room._spawn_popup("FASE INCORRECTA", self.hitbox.centerx, self.hitbox.top - 6, 0.5, (220, 100, 100))
            return False

        self.is_activated = True
        self.animation.reset()
        
        if room:
            room.camera.shake(3.5, 0.25)
            sfx_key = "phase_shift_past" if self.phase == "green" else "phase_shift_future"
            if sfx_key in settings.SOUNDS:
                settings.SOUNDS[sfx_key].play()
            room.spawn_dust(self.hitbox.centerx, self.hitbox.bottom, count=16)
            room._spawn_popup("¡ACTIVADO!", self.hitbox.centerx, self.hitbox.top - 8, 0.7, self.glow_color)

        if self.on_activated:
            self.on_activated(self)

        return True

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        rx = int(self.x - camera_x)
        ry = int(self.y - camera_y)

        pulse_alpha = int(120 + 55 * math.sin(self.pulse_timer))
        glow_radius = 28 if not self.is_activated else 48
        core_pos = (rx + self.width // 2, ry + 105)

        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.glow_color, pulse_alpha // 2), (glow_radius, glow_radius), glow_radius)
        pygame.draw.circle(glow_surf, (*self.glow_color, pulse_alpha), (glow_radius, glow_radius), glow_radius // 2)
        surface.blit(glow_surf, (core_pos[0] - glow_radius, core_pos[1] - glow_radius))

        if self._frames:
            frame_surf = self.animation.get_current_frame()
            surface.blit(frame_surf, (rx, ry))

            gem_surf = pygame.Surface((12, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(gem_surf, (*self.glow_color, 230), (0, 0, 12, 16))
            pygame.draw.ellipse(gem_surf, (255, 255, 255, 240), (3, 3, 6, 8))
            surface.blit(gem_surf, (rx + 21, ry + 98))


