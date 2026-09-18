from typing import Optional, List, Tuple, Dict
import math
import pygame
from gale.animation import Animation

import settings


class LightMonolith:
    _SCALED_FRAMES_CACHE: Dict[float, List[pygame.Surface]] = {}

    def __init__(self, x: float, y: float, phase: str = "green", on_activated=None, scale: float = 1.0) -> None:
        self.x: float = x
        self.y: float = y
        self.phase: str = phase
        self.on_activated = on_activated
        self.scale: float = scale

        self.width: int = max(16, int(54 * scale))
        self.height: int = max(32, int(169 * scale))
        self.hitbox: pygame.Rect = pygame.Rect(
            int(x + 7 * scale),
            int(y + 60 * scale),
            max(16, int(40 * scale)),
            max(20, int(105 * scale))
        )

        self.is_activated: bool = False
        self.pulse_timer: float = 0.0

        raw_frames = settings.FRAMES.get("monolith_frames", [])
        if scale != 1.0 and raw_frames:
            if scale not in self._SCALED_FRAMES_CACHE:
                self._SCALED_FRAMES_CACHE[scale] = [
                    pygame.transform.scale(f, (self.width, self.height)) for f in raw_frames
                ]
            self._frames = self._SCALED_FRAMES_CACHE[scale]
        else:
            self._frames = raw_frames

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
        glow_radius = int((28 if not self.is_activated else 48) * self.scale)
        glow_radius = max(14, glow_radius)
        core_pos = (rx + self.width // 2, ry + int(105 * self.scale))

        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.glow_color, pulse_alpha // 2), (glow_radius, glow_radius), glow_radius)
        pygame.draw.circle(glow_surf, (*self.glow_color, pulse_alpha), (glow_radius, glow_radius), glow_radius // 2)
        surface.blit(glow_surf, (core_pos[0] - glow_radius, core_pos[1] - glow_radius))

        if self._frames:
            frame_surf = self.animation.get_current_frame()
            surface.blit(frame_surf, (rx, ry))

            gem_w = max(6, int(12 * self.scale))
            gem_h = max(8, int(16 * self.scale))
            gem_surf = pygame.Surface((gem_w, gem_h), pygame.SRCALPHA)
            pygame.draw.ellipse(gem_surf, (*self.glow_color, 230), (0, 0, gem_w, gem_h))
            pygame.draw.ellipse(gem_surf, (255, 255, 255, 240), (max(1, int(3 * self.scale)), max(1, int(3 * self.scale)), max(2, int(6 * self.scale)), max(3, int(8 * self.scale))))
            surface.blit(gem_surf, (rx + int(21 * self.scale), ry + int(98 * self.scale)))
