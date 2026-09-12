"""
Chrono Blight
"""

from typing import Any
import pygame

from gale.state import BaseState
from gale.input_handler import InputData

import settings
from src.definitions import entity as entity_defs
from src.entities.Player import Player
from src.world.Camera import Camera
from src.ui.HUD import HUD


class PlayState(BaseState):

    TILE_SIZE: int = settings.TILE_SIZE
    MAP_COLS: int = 78
    MAP_ROWS: int = 13
    MAP_WIDTH: int = MAP_COLS * TILE_SIZE    # 1248 px
    MAP_HEIGHT: int = MAP_ROWS * TILE_SIZE   # 208 px
    FLOOR_ROW: int = 10
    FLOOR_Y: float = float(FLOOR_ROW * TILE_SIZE)

    def enter(self, **params: Any) -> None:
        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.camera.set_map_bounds(self.MAP_WIDTH, self.MAP_HEIGHT)

        spawn_x = 48.0
        spawn_y = float(self.FLOOR_Y - entity_defs.PLAYER_HIT_H)
        self.player = Player(spawn_x, spawn_y, floor_y=self.FLOOR_Y, map_w=float(self.MAP_WIDTH))

        self._init_room_graphics()
        self.hud = HUD()

    def _create_radial_glow(self, radius: int, color_rgb: tuple[int, int, int], max_alpha: int = 40) -> pygame.Surface:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(max_alpha * (1.0 - (r / radius) ** 1.5))
            pygame.draw.circle(surf, (*color_rgb, alpha), (radius, radius), r)
        return surf

    def _init_room_graphics(self) -> None:
        sky_h = int(self.FLOOR_Y)
        self.sky_surfaces = {}

        palettes = {
            "red":   ((42, 28, 36), (78, 50, 62)),
            "green": ((20, 30, 46), (50, 72, 102)),
        }
        for phase, (top_col, bot_col) in palettes.items():
            sky = pygame.Surface((self.MAP_WIDTH, sky_h))
            for y in range(sky_h):
                t = y / max(1, sky_h)
                r = int(top_col[0] + (bot_col[0] - top_col[0]) * t)
                g = int(top_col[1] + (bot_col[1] - top_col[1]) * t)
                b = int(top_col[2] + (bot_col[2] - top_col[2]) * t)
                pygame.draw.line(sky, (r, g, b), (0, y), (self.MAP_WIDTH, y))
            self.sky_surfaces[phase] = sky

        self.glow_surfaces = {
            "red":   self._create_radial_glow(36, (255, 100, 100), max_alpha=40),
            "green": self._create_radial_glow(36, (70, 230, 140), max_alpha=45),
        }

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:

        self.player.update(dt)
        self.camera.update(self.player.hitbox.centerx,self.player.hitbox.centery,)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            from src.states.game.PauseState import PauseState
            self.state_machine.push(PauseState(self.state_machine))

        elif input_id == "phase_shift" and input_data.pressed:
            if self.player.toggle_phase():
                from src.states.game.PhaseShiftState import PhaseShiftState
                self.state_machine.push(PhaseShiftState(self.state_machine))

        elif input_id == "prev_form" and input_data.pressed:
            self.player.cycle_skin(-1)

        elif input_id in ("next_form", "toggle_morph") and input_data.pressed:
            self.player.cycle_skin(1)

        else:
            self.player.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        cam_x, cam_y = self.camera.get_offset()
        phase = self.player.phase_color

        if phase == "red":
            ground_top_color = (175, 95, 95)
            ground_body_color = (65, 45, 54)
            grid_line_color = (90, 60, 72)
            wall_color = (130, 65, 65)
        else:
            ground_top_color = (95, 155, 205)
            ground_body_color = (36, 52, 74)
            grid_line_color = (52, 75, 105)
            wall_color = (60, 100, 150)

        surface.fill((10, 10, 15))

        room_screen_x = int(0 - cam_x)
        room_screen_y = int(0 - cam_y)
        sky_surf = self.sky_surfaces.get(phase)
        if sky_surf:
            surface.blit(sky_surf, (room_screen_x, room_screen_y))

        pygame.draw.rect(surface, wall_color, pygame.Rect(room_screen_x, room_screen_y, 4, self.MAP_HEIGHT))
        pygame.draw.rect(surface, wall_color, pygame.Rect(room_screen_x + self.MAP_WIDTH - 4, room_screen_y, 4, self.MAP_HEIGHT))

        floor_screen_y = int(self.FLOOR_Y - cam_y)
        floor_height = self.MAP_HEIGHT - int(self.FLOOR_Y)
        floor_rect = pygame.Rect(room_screen_x, floor_screen_y, self.MAP_WIDTH, floor_height)
        pygame.draw.rect(surface, ground_body_color, floor_rect)

        pygame.draw.line(surface, ground_top_color, (room_screen_x, floor_screen_y), (room_screen_x + self.MAP_WIDTH, floor_screen_y), 2)

        start_col = max(0, int(cam_x // self.TILE_SIZE))
        end_col = min(self.MAP_COLS, int((cam_x + settings.VIRTUAL_WIDTH) // self.TILE_SIZE) + 2)

        for col in range(start_col, end_col):
            tile_screen_x = int(col * self.TILE_SIZE - cam_x)
            pygame.draw.line(
                surface,
                grid_line_color,
                (tile_screen_x, floor_screen_y),
                (tile_screen_x, floor_screen_y + floor_height),
                1
            )
            sub_y = floor_screen_y + self.TILE_SIZE
            pygame.draw.line(
                surface,
                grid_line_color,
                (tile_screen_x, sub_y),
                (tile_screen_x + self.TILE_SIZE, sub_y),
                1
            )

        glow_surf = self.glow_surfaces.get(phase)
        if glow_surf:
            player_center_x = int(self.player.hitbox.centerx - cam_x)
            player_center_y = int(self.player.hitbox.centery - cam_y)
            surface.blit(glow_surf, (player_center_x - 36, player_center_y - 36))

        self.player.render(surface, cam_x, cam_y)

        self.hud.render(surface, self.player, cam_x, cam_y)
