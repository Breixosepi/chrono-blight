import math
import random
from typing import TYPE_CHECKING, List, Dict, Any, Optional

import pygame
import settings

if TYPE_CHECKING:
    from src.world.Room import Room


class LavaShower:
    """
    Cascada de lava/ácido que desciende desde el techo utilizando el mismo renderizado,
    ondas sinusoidales, crestas brillantes y partículas de RisingHazard.
    """

    ZONES = [
        {"name": "Izquierda", "min_x": 64, "max_x": 224},
        {"name": "Centro",    "min_x": 240, "max_x": 400},
        {"name": "Derecha",   "min_x": 416, "max_x": 576},
    ]

    def __init__(self, room: "Room"):
        self.room = room
        self.state = "cooldown"  # "cooldown", "warning", "active", "retracting"
        self.timer = 3.5
        self.cooldown_duration = 5.0
        self.warning_duration = 1.0
        self.active_duration = 2.8

        self.current_zone_idx = 0
        self.current_zone = self.ZONES[0]
        self.current_lava_y = 0.0
        self.wave_timer = 0.0
        self.damage_tick_timer = 0.0

        self.liquid_particles: List[Dict[str, Any]] = []

    def reset(self) -> None:
        self.state = "cooldown"
        self.timer = 3.5
        self.current_lava_y = 0.0
        self.liquid_particles.clear()

    def update(self, dt: float) -> None:
        self.wave_timer += dt * 3.0
        self.timer -= dt

        # Actualizar partículas de lava
        for p in self.liquid_particles[:]:
            p["life"] -= dt
            p["y"] += p["vy"] * dt
            p["x"] += p["vx"] * dt
            if p["life"] <= 0 or p["y"] > self.room.MAP_HEIGHT:
                self.liquid_particles.remove(p)

        if self.state == "cooldown":
            self.current_lava_y = 0.0
            if self.timer <= 0:
                # Localizar la posición actual del jugador y fijar la zona de impacto
                player_x = self.room.player.hitbox.centerx
                zone_w = 110.0
                min_x = max(48.0, min(float(self.room.MAP_WIDTH) - 48.0 - zone_w, player_x - (zone_w / 2.0)))
                max_x = min_x + zone_w
                self.current_zone = {"min_x": min_x, "max_x": max_x}

                self.state = "warning"
                self.timer = self.warning_duration

        elif self.state == "warning":
            # Gotas y burbujas de advertencia cayendo del techo
            min_x = self.current_zone["min_x"]
            max_x = self.current_zone["max_x"]
            for _ in range(3):
                self.liquid_particles.append({
                    "x": random.uniform(min_x, max_x),
                    "y": random.uniform(0, 24),
                    "vx": random.uniform(-15, 15),
                    "vy": random.uniform(90, 180),
                    "life": 0.55,
                    "max_life": 0.55,
                    "radius": random.choice([1, 2]),
                    "color": random.choice([(255, 180, 50), (220, 50, 40), (255, 90, 40)]),
                })

            if self.timer <= 0:
                self.state = "active"
                self.timer = self.active_duration
                self.current_lava_y = 0.0
                self.damage_tick_timer = 0.0
                self.room.camera.shake(2.5, 0.2)

        elif self.state == "active":
            min_x = self.current_zone["min_x"]
            max_x = self.current_zone["max_x"]
            floor_y = float(self.room.MAP_HEIGHT)

            # La lava desciende rápidamente desde el techo hasta el suelo
            descend_speed = 320.0
            if self.current_lava_y < floor_y:
                self.current_lava_y = min(floor_y, self.current_lava_y + descend_speed * dt)

            # Spawn de burbujas incandescentes en el frente de la cascada
            for _ in range(4):
                self.liquid_particles.append({
                    "x": random.uniform(min_x, max_x),
                    "y": max(4.0, self.current_lava_y + random.uniform(-10, 8)),
                    "vx": random.uniform(-25, 25),
                    "vy": random.uniform(-40, 60),
                    "life": 0.45,
                    "max_life": 0.45,
                    "radius": random.choice([2, 3, 4]),
                    "color": random.choice([(255, 220, 90), (255, 120, 30), (200, 30, 20)]),
                })

            # Daño continuo si el jugador toca la cascada
            self.damage_tick_timer -= dt
            player = self.room.player
            if (
                player.hitbox.right > min_x
                and player.hitbox.left < max_x
                and player.hitbox.top <= self.current_lava_y
            ):
                if self.damage_tick_timer <= 0:
                    self.damage_tick_timer = 0.45
                    if player.invulnerable_timer <= 0:
                        player.take_damage(12)
                        self.room.camera.shake(3.0, 0.15)
                        self.room._spawn_popup(
                            "-12",
                            player.hitbox.centerx,
                            player.hitbox.top - 10,
                            0.6,
                            (255, 60, 60),
                        )

            if self.timer <= 0:
                self.state = "cooldown"
                self.timer = self.cooldown_duration

    def render(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        min_x = int(self.current_zone["min_x"])
        max_x = int(self.current_zone["max_x"])
        zone_w = max_x - min_x
        draw_x = int(min_x - cam_x)

        # 1. Renderizar partículas
        for p in self.liquid_particles:
            px = int(p["x"] - cam_x)
            py = int(p["y"] - cam_y)
            pygame.draw.circle(surface, p["color"], (px, py), p["radius"])

        # 2. Renderizado de advertencia
        if self.state == "warning":
            warn_surf = pygame.Surface((zone_w, int(self.room.MAP_HEIGHT)), pygame.SRCALPHA)
            alpha = int(45 + 35 * math.sin(self.wave_timer * 3))
            warn_surf.fill((255, 70, 20, alpha))
            surface.blit(warn_surf, (draw_x, int(0 - cam_y)))

        # 3. Renderizado idéntico a RisingHazard (Lava de cuerpo completo con crestas)
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

            # Cuerpo de la cascada de lava descendente
            lava_surf = pygame.Surface((zone_w, current_h), pygame.SRCALPHA)
            lava_surf.fill(body_color)
            surface.blit(lava_surf, (draw_x, int(0 - cam_y)))

            # Resplandor en la punta inferior de la cascada
            leading_screen_y = int(self.current_lava_y - cam_y)
            glow_surf = pygame.Surface((zone_w, 14), pygame.SRCALPHA)
            glow_surf.fill(glow_color)
            surface.blit(glow_surf, (draw_x, max(0, leading_screen_y - 7)))

            # Cresta de onda sinusoidal en la punta inferior
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
