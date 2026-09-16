"""
Chrono Blight - Liquid Hazard (Rising / Falling)
"""
from typing import TYPE_CHECKING, List, Dict, Any, Optional
import math
import random
import pygame
from gale.state import StateMachine
from gale.particle_system import ParticleSystem
from gale.text import render_text

import settings
from src.states.hazard import (
    HazardBaseState,
    InactiveState,
    TriggeredState,
    MovingState,
    EscapedState,
)

if TYPE_CHECKING:
    from src.world.Room import Room
    from src.entities.Player import Player

class RisingHazard:
    STATE_INACTIVE = "inactive"
    STATE_TRIGGERED = "triggered"
    STATE_MOVING = "moving"  
    STATE_ESCAPED = "escaped"

    def __init__(
        self,
        room: "Room",
        speed: float = 18.0,
        trigger_x: float = 50.0,
        delay: float = 2.5,
        escape_y: Optional[float] = None,
    ) -> None:
        self.room = room
        self.speed = speed
        self.trigger_x = trigger_x
        self.delay_max = delay

        tile_size = float(getattr(room, "TILE_SIZE", 16))
        self.escape_y = escape_y if escape_y is not None else (2.0 * tile_size)

        self.velocity_y = -self.speed  
        self.triggered_text = "¡TRAMPA ACTIVADA!"
        self.moving_text = "¡EL LÍQUIDO SUBE!"
        self.escaped_text = "¡ESCAPASTE!"
        self.escaped_timer_duration = 5.0
        self.target_color = None

        self.trigger_rect = pygame.Rect(int(trigger_x), 550, 1000, 200)

        fire_start_y = float(room.MAP_HEIGHT)

        for layer in room.map_data.get("layers", []):
            if layer.get("type") == "objectgroup" or "objects" in layer:
                for obj in layer.get("objects", []):
                    obj_name = (obj.get("name") or "").lower().strip()
                    
                    if obj_name in ("fire", "lava", "magma", "acid"):
                        fire_start_y = float(obj.get("y", room.MAP_HEIGHT))
                        
                    elif obj_name == "hazard_trigger":
                        self.trigger_rect = pygame.Rect(
                            int(obj.get("x", 0)),
                            int(obj.get("y", 0)),
                            int(obj.get("width", 16)),
                            int(obj.get("height", 16))
                        )

        self.start_y = fire_start_y
        self.current_y = fire_start_y
        self.wave_timer = 0.0
        self.liquid_particles: List[Dict[str, Any]] = []

        self.gate_particle_system: Optional[ParticleSystem] = None
        self.gate_x = 4.0
        self.gate_width = 24.0
        self.gate_open_y = 540.0
        self.gate_closed_y = 576.0
        self.gate_current_y = self.gate_open_y
        self.gate_landed = False

        self.alert_timer = 0.0
        self.alert_text = ""

        self.hud_x = settings.VIRTUAL_WIDTH - 12
        self.hud_y = 16
        self.hud_w = 4
        self.hud_h = 64

        self.state_machine = StateMachine({
            self.STATE_INACTIVE: lambda sm: InactiveState(self, sm),
            self.STATE_TRIGGERED: lambda sm: TriggeredState(self, sm),
            self.STATE_MOVING: lambda sm: MovingState(self, sm),
            self.STATE_ESCAPED: lambda sm: EscapedState(self, sm),
        })
        self.state_machine.change(self.STATE_INACTIVE)

    @property
    def state(self) -> str:
        current = self.state_machine.current
        if isinstance(current, HazardBaseState):
            return current.state_name
        return self.STATE_INACTIVE

    @state.setter
    def state(self, new_state: str) -> None:
        self.state_machine.change(new_state)

    def spawn_gate_impact_particles(self) -> None:
        impact_x = self.gate_x + self.gate_width / 2
        impact_y = self.gate_closed_y + 32
        ps = ParticleSystem(impact_x, impact_y, n=14)
        ps.set_life_time(0.2, 0.45)
        ps.set_linear_acceleration(-40.0, -60.0, 40.0, -10.0)
        ps.set_area_spread(10.0, 2.0)
        ps.set_colors([
            pygame.Color(200, 210, 225, 240),
            pygame.Color(140, 150, 165, 220),
            pygame.Color(90, 95, 110, 200),
        ])
        ps.generate()
        self.gate_particle_system = ps

    def update(self, dt: float, player: "Player") -> None:
        self.wave_timer += dt * 3.5
        if self.alert_timer > 0.0:
            self.alert_timer = max(0.0, self.alert_timer - dt)

        current_state = self.state_machine.current
        if isinstance(current_state, HazardBaseState):
            current_state.update_with_player(dt, player)

        if self.gate_particle_system is not None:
            self.gate_particle_system.update(dt)
            if len(self.gate_particle_system.particles) == 0:
                self.gate_particle_system = None

        self._update_liquid_particles(dt, player.phase_color)

    def _update_liquid_particles(self, dt: float, phase: str) -> None:
        if self.state in (self.STATE_MOVING, self.STATE_TRIGGERED, self.STATE_ESCAPED):
            if random.random() < 0.4:
                self.liquid_particles.append({
                    "x": random.uniform(0, self.room.MAP_WIDTH),
                    "y": self.current_y + random.uniform(-2.0, 4.0),
                    "vx": random.uniform(-6.0, 6.0),
                    "vy": random.uniform(-25.0, -10.0) if phase == "green" else random.uniform(-35.0, -15.0),
                    "life": random.uniform(0.5, 0.9),
                    "max_life": 0.9,
                    "radius": random.choice([1, 1, 2]),
                })

        for p in self.liquid_particles[:]:
            p["life"] -= dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["life"] <= 0.0:
                self.liquid_particles.remove(p)

    def check_player_hit(self, player: "Player") -> bool:
        if self.state in (self.STATE_INACTIVE, self.STATE_ESCAPED):
            return False
        if player.hitbox.bottom >= (self.current_y + 4):
            return True
        return False

    def reset(self) -> None:
        self.state_machine.change(self.STATE_INACTIVE)

    def render_world(self, surface: pygame.Surface, cam_x: float, cam_y: float, phase: str) -> None:
        self._render_gate(surface, cam_x, cam_y)
        
        if self.gate_particle_system is not None:
            for particle in self.gate_particle_system.particles:
                if self.gate_particle_system.timer < particle.life_time:
                    screen_px = int(particle.x - cam_x)
                    screen_py = int(particle.y - cam_y)
                    if 0 <= screen_px < settings.VIRTUAL_WIDTH and 0 <= screen_py < settings.VIRTUAL_HEIGHT:
                        p_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
                        p_surf.fill(particle.color)
                        surface.blit(p_surf, (screen_px, screen_py))

        screen_lava_y = int(self.current_y - cam_y)
        if screen_lava_y < settings.VIRTUAL_HEIGHT:
            self._render_liquid(surface, screen_lava_y, cam_x, cam_y, phase)

        part_color = (120, 255, 170) if phase == "green" else (255, 140, 60)
        for p in self.liquid_particles:
            px = int(p["x"] - cam_x)
            py = int(p["y"] - cam_y)
            if 0 <= px < settings.VIRTUAL_WIDTH and 0 <= py < settings.VIRTUAL_HEIGHT:
                pygame.draw.circle(surface, part_color, (px, py), p["radius"])

    def _render_gate(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        gx = int(self.gate_x - cam_x)
        gy = int(self.gate_current_y - cam_y)
        gw = int(self.gate_width)
        gh = 36
        pygame.draw.rect(surface, (45, 48, 55), (gx, gy, gw, 3))
        pygame.draw.rect(surface, (70, 75, 85), (gx, gy, gw, 1))

        num_bars = 5
        bar_spacing = gw // num_bars
        for i in range(num_bars):
            bx = gx + i * bar_spacing + 2
            pygame.draw.rect(surface, (60, 64, 75), (bx, gy, 2, gh))
            pygame.draw.rect(surface, (110, 115, 130), (bx, gy, 1, gh))
            pygame.draw.polygon(surface, (130, 135, 150), [
                (bx - 1, gy + gh),
                (bx + 1, gy + gh + 4),
                (bx + 3, gy + gh),
            ])
        pygame.draw.rect(surface, (50, 54, 62), (gx, gy + gh // 2, gw, 2))

    def _render_liquid(
        self,
        surface: pygame.Surface,
        screen_lava_y: int,
        cam_x: float,
        cam_y: float,
        phase: str,
    ) -> None:
        fill_top = max(0, screen_lava_y)
        fill_height = settings.VIRTUAL_HEIGHT - fill_top
        if fill_height <= 0:
            return

        if self.target_color:
            body_color = (*self.target_color, 240)
            crest_bright = (min(255, self.target_color[0]+50), min(255, self.target_color[1]+50), min(255, self.target_color[2]+50))
            crest_dark = (max(0, self.target_color[0]-50), max(0, self.target_color[1]-50), max(0, self.target_color[2]-50))
            glow_color = (*self.target_color, 75)
        elif phase == "green":
            body_color = (12, 44, 28, 235)
            crest_bright = (100, 255, 160)
            crest_dark = (25, 170, 85)
            glow_color = (60, 240, 130, 70)
        else:
            body_color = (55, 12, 22, 240)
            crest_bright = (255, 180, 50)
            crest_dark = (220, 50, 40)
            glow_color = (255, 90, 40, 75)

        liquid_surf = pygame.Surface((settings.VIRTUAL_WIDTH, fill_height), pygame.SRCALPHA)
        liquid_surf.fill(body_color)
        surface.blit(liquid_surf, (0, fill_top))

        if 0 <= screen_lava_y < settings.VIRTUAL_HEIGHT:
            glow_surf = pygame.Surface((settings.VIRTUAL_WIDTH, 12), pygame.SRCALPHA)
            glow_surf.fill(glow_color)
            surface.blit(glow_surf, (0, max(0, screen_lava_y - 6)))

        points_bright = []
        points_dark = []
        step = 4
        for sx in range(0, settings.VIRTUAL_WIDTH + step, step):
            world_x = sx + cam_x
            wave = (
                math.sin(world_x * 0.06 + self.wave_timer) * 2.5
                + math.sin(world_x * 0.12 - self.wave_timer * 1.5) * 1.2
            )
            sy = screen_lava_y + int(wave)
            points_bright.append((sx, sy))
            points_dark.append((sx, sy + 2))

        if len(points_bright) >= 2:
            pygame.draw.lines(surface, crest_dark, False, points_dark, 2)
            pygame.draw.lines(surface, crest_bright, False, points_bright, 1)

    def render_hud(self, surface: pygame.Surface, player: "Player") -> None:
        if self.alert_timer > 0.0:
            if int(self.alert_timer * 8) % 2 == 0:
                col = (255, 230, 80) if self.state == self.STATE_TRIGGERED else (255, 70, 70)
                if self.state == self.STATE_ESCAPED:
                    col = (100, 255, 140)
                render_text(
                    surface,
                    self.alert_text,
                    settings.FONTS["title"],
                    settings.VIRTUAL_WIDTH // 2,
                    36,
                    col,
                    center=True,
                    shadowed=True,
                )

        if self.state in (self.STATE_TRIGGERED, self.STATE_MOVING, self.STATE_ESCAPED):
            ix = self.hud_x
            iy = self.hud_y
            iw = self.hud_w
            ih = self.hud_h

            bar_bg = pygame.Surface((iw + 2, ih + 2), pygame.SRCALPHA)
            bar_bg.fill((15, 18, 25, 190))
            pygame.draw.rect(bar_bg, (50, 55, 70, 220), (0, 0, iw + 2, ih + 2), 1)
            surface.blit(bar_bg, (ix - 1, iy - 1))

            map_h = float(self.room.MAP_HEIGHT)
            phase = player.phase_color

            lava_progress = max(0.0, min(1.0, (map_h - self.current_y) / map_h))
            lava_bar_h = int(lava_progress * ih)

            if lava_bar_h > 0:
                if self.target_color:
                    lava_col = self.target_color
                    crest_col = (min(255, lava_col[0]+50), min(255, lava_col[1]+50), min(255, lava_col[2]+50))
                else:
                    lava_col = (50, 220, 110) if phase == "green" else (240, 70, 50)
                    crest_col = (180, 255, 200) if phase == "green" else (255, 200, 100)
                    
                pygame.draw.rect(surface, lava_col, (ix, iy + ih - lava_bar_h, iw, lava_bar_h))
                pygame.draw.rect(surface, crest_col, (ix, iy + ih - lava_bar_h, iw, 1))

            player_progress = max(0.0, min(1.0, (map_h - player.hitbox.centery) / map_h))
            player_py = iy + ih - int(player_progress * ih)

            dist = self.current_y - player.hitbox.bottom
            is_close = (dist < 45.0) and (self.state == self.STATE_MOVING)
            
            if is_close and (int(pygame.time.get_ticks() / 150) % 2 == 0):
                pygame.draw.rect(surface, (255, 50, 50), (ix - 2, player_py - 1, iw + 4, 3))
            else:
                marker_col = (80, 200, 255)
                pygame.draw.rect(surface, marker_col, (ix - 1, player_py - 1, iw + 2, 3))
                pygame.draw.rect(surface, (255, 255, 255), (ix, player_py, iw, 1))