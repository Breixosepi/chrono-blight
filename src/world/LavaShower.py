"""
Chrono Blight - Lava Shower
"""
import math
import random
from typing import TYPE_CHECKING, List, Dict, Any, Optional
import pygame
from gale.timer import Timer, After

if TYPE_CHECKING:
    from src.world.Room import Room

class LavaShower:
    def __init__(self, room: "Room"):
        self.room = room
        self.state = "cooldown"
        
        self.cooldown_duration = 5.0
        self.warning_duration = 1.0
        self.active_duration = 2.8
        
        self.current_zone = {"min_x": 100.0, "max_x": 210.0}
        self.current_lava_y = 0.0
        self.wave_timer = 0.0
        
        self.liquid_particles: List[Dict[str, Any]] = []
        self.phase_timer: Optional[After] = None
        self.damage_timer: Optional[After] = None
        self._start_cooldown(3.5)

    def reset(self) -> None:
        self.current_lava_y = 0.0
        self.liquid_particles.clear()
        self._cancel_timers()
        self._start_cooldown(3.5)

    def _cancel_timers(self) -> None:
        if self.phase_timer:
            self.phase_timer.remove()
            self.phase_timer = None
        if self.damage_timer:
            self.damage_timer.remove()
            self.damage_timer = None

    def _start_cooldown(self, duration: float = None) -> None:
        self.state = "cooldown"
        self.current_lava_y = 0.0
        duration = duration if duration is not None else self.cooldown_duration
        self.phase_timer = Timer.after(duration, self._start_warning)

    def _start_warning(self) -> None:
        player_x = self.room.player.hitbox.centerx
        zone_w = 110.0
        min_x = max(48.0, min(float(self.room.MAP_WIDTH) - 48.0 - zone_w, player_x - (zone_w / 2.0)))
        
        self.current_zone = {"min_x": min_x, "max_x": min_x + zone_w}
        self.state = "warning"
        
        self.phase_timer = Timer.after(self.warning_duration, self._start_active)

    def _start_active(self) -> None:
        self.state = "active"
        self.current_lava_y = 0.0
        self.room.camera.shake(2.5, 0.2)
        
        self.phase_timer = Timer.after(self.active_duration, self._start_cooldown)
        
        self.damage_timer = Timer.every(0.45, self._apply_damage_tick)

    def _apply_damage_tick(self) -> None:
        """Aplica daño si el jugador está dentro de la cascada activa."""
        if self.state != "active":
            return
            
        player = self.room.player
        min_x = self.current_zone["min_x"]
        max_x = self.current_zone["max_x"]
        
        if (player.hitbox.right > min_x and 
            player.hitbox.left < max_x and 
            player.hitbox.top <= self.current_lava_y):
            
            if player.invulnerable_timer <= 0:
                player.take_damage(12)
                self.room.camera.shake(3.0, 0.15)
                self.room._spawn_popup("-12", player.hitbox.centerx, player.hitbox.top - 10, 0.6, (255, 60, 60))

    def update(self, dt: float) -> None:
        self.wave_timer += dt * 3.0
        
        for p in self.liquid_particles[:]:
            p["life"] -= dt
            p["y"] += p["vy"] * dt
            p["x"] += p["vx"] * dt
            if p["life"] <= 0 or p["y"] > self.room.MAP_HEIGHT:
                self.liquid_particles.remove(p)

        min_x = self.current_zone["min_x"]
        max_x = self.current_zone["max_x"]

        if self.state == "warning":
            for _ in range(3):
                self.liquid_particles.append({
                    "x": random.uniform(min_x, max_x),
                    "y": random.uniform(0, 24),
                    "vx": random.uniform(-15, 15),
                    "vy": random.uniform(90, 180),
                    "life": 0.55,
                    "radius": random.choice([1, 2]),
                    "color": random.choice([(255, 180, 50), (220, 50, 40), (255, 90, 40)]),
                })
                
        elif self.state == "active":
            floor_y = float(self.room.MAP_HEIGHT)
            descend_speed = 320.0
            
            if self.current_lava_y < floor_y:
                self.current_lava_y = min(floor_y, self.current_lava_y + descend_speed * dt)
                
            for _ in range(4):
                self.liquid_particles.append({
                    "x": random.uniform(min_x, max_x),
                    "y": max(4.0, self.current_lava_y + random.uniform(-10, 8)),
                    "vx": random.uniform(-25, 25),
                    "vy": random.uniform(-40, 60),
                    "life": 0.45,
                    "radius": random.choice([2, 3, 4]),
                    "color": random.choice([(255, 220, 90), (255, 120, 30), (200, 30, 20)]),
                })

    def render(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        min_x = int(self.current_zone["min_x"])
        max_x = int(self.current_zone["max_x"])
        zone_w = max_x - min_x
        draw_x = int(min_x - cam_x)

        for p in self.liquid_particles:
            px = int(p["x"] - cam_x)
            py = int(p["y"] - cam_y)
            pygame.draw.circle(surface, p["color"], (px, py), p["radius"])

        if self.state == "warning":
            warn_surf = pygame.Surface((zone_w, int(self.room.MAP_HEIGHT)), pygame.SRCALPHA)
            alpha = int(45 + 35 * math.sin(self.wave_timer * 3))
            warn_surf.fill((255, 70, 20, alpha))
            surface.blit(warn_surf, (draw_x, int(0 - cam_y)))
            
        elif self.state == "active" and self.current_lava_y > 4.0:
            phase = self.room.player.phase_color
            if phase == "green":
                body_color = (12, 44, 28, 235)
                crest_bright = (100, 255, 160)
                crest_dark = (25, 170, 85)
                glow_color = (60, 240, 130, 80)
            else:
                body_color = (55, 12, 22, 240)
                crest_bright = (255, 180, 50)
                crest_dark = (220, 50, 40)
                glow_color = (255, 90, 40, 85)

            current_h = int(self.current_lava_y)
            lava_surf = pygame.Surface((zone_w, current_h), pygame.SRCALPHA)
            lava_surf.fill(body_color)
            surface.blit(lava_surf, (draw_x, int(0 - cam_y)))

            leading_screen_y = int(self.current_lava_y - cam_y)
            glow_surf = pygame.Surface((zone_w, 14), pygame.SRCALPHA)
            glow_surf.fill(glow_color)
            surface.blit(glow_surf, (draw_x, max(0, leading_screen_y - 7)))

            points_bright = []
            points_dark = []
            step = 4
            for rx in range(0, zone_w + step, step):
                world_x = min_x + rx
                wave = (
                    math.sin(world_x * 0.08 + self.wave_timer) * 2.5
                    + math.sin(world_x * 0.16 - self.wave_timer * 1.5) * 1.2
                )
                sy = leading_screen_y + int(wave)
                sx = draw_x + rx
                points_bright.append((sx, sy))
                points_dark.append((sx, sy + 2))

            if len(points_bright) >= 2:
                pygame.draw.lines(surface, crest_dark, False, points_dark, 2)
                pygame.draw.lines(surface, crest_bright, False, points_bright, 1)