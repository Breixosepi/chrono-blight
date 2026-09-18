"""
Chrono Blight - Splash Screen State
"""
from typing import Any, Optional
import pygame
import numpy as np
from gale.state import BaseState
from gale.input_handler import InputData
from src.states.game.TitleState import TitleState
import settings

class SplashState(BaseState):
    DURATION_PAST: float = 1.5 
    DURATION_FUTURE: float = 1.5  

    def enter(self, **params: Any) -> None:
        self.timer: float = 0.0
        self.phase: str = "past"
        self.is_done: bool = False
        self.flash_alpha: float = 0.0
        self.fade_out_alpha: float = 0.0
        self._sound_played: bool = False

        self._flash_surf = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )

        self._past_bg = self._create_radial_gradient(
            outer_color=(23, 94, 67),  
            center_color=(0, 0, 0),       
        )
        self._future_bg = self._create_radial_gradient(
            outer_color=(99, 18, 25),    
            center_color=(0, 0, 0),         
        )
        self._logo_surf, self._logo_pos = self._prepare_crisp_logo()

    def _create_radial_gradient(
        self,
        center_color: tuple[int, int, int],
        outer_color: tuple[int, int, int],
    ) -> pygame.Surface:
        w, h = settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT
        cx, cy = w / 2.0, h / 2.0

        y_coords, x_coords = np.ogrid[:h, :w]
        dist = np.sqrt(((x_coords - cx) / 1.15) ** 2 + (y_coords - cy) ** 2)
        max_r = 135.0
        norm = np.clip(dist / max_r, 0.0, 1.0)
        factor = 1.0 - (norm ** 1.35)

        r = outer_color[0] + factor * (center_color[0] - outer_color[0])
        g = outer_color[1] + factor * (center_color[1] - outer_color[1])
        b = outer_color[2] + factor * (center_color[2] - outer_color[2])

        rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
        rgb_trans = np.transpose(rgb, (1, 0, 2))

        surf = pygame.surfarray.make_surface(rgb_trans)
        return surf

    def _prepare_crisp_logo(self) -> tuple[Optional[pygame.Surface], tuple[int, int]]:
        raw_logo = settings.TEXTURES.get("logo")
        if not raw_logo:
            raw_logo = settings.TEXTURES.get("logo_past")
            if not raw_logo:
                return None, (0, 0)

        bbox = raw_logo.get_bounding_rect()
        cropped = raw_logo.subsurface(bbox)

        target_w = 150
        target_h = int(target_w * (bbox.height / bbox.width))
        scaled_logo = pygame.transform.smoothscale(cropped, (target_w, target_h))

        pos_x = (settings.VIRTUAL_WIDTH - target_w) // 2
        pos_y = (settings.VIRTUAL_HEIGHT - target_h) // 2

        return scaled_logo, (pos_x, pos_y)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed and not self.is_done:
            self._finish_splash()

    def update(self, dt: float) -> None:
        if self.is_done:
            return

        self.timer += dt

        if self.flash_alpha > 0.0:
            self.flash_alpha = max(0.0, self.flash_alpha - dt * 600.0)

        if self.timer >= self.DURATION_PAST and self.phase == "past":
            self.phase = "future"
            self.flash_alpha = 180.0
            if not self._sound_played:
                self._sound_played = True
                if "phase_shift_future" in settings.SOUNDS:
                    settings.SOUNDS["phase_shift_future"].play()
                elif "change" in settings.SOUNDS:
                    settings.SOUNDS["change"].play()

        total_duration = self.DURATION_PAST + self.DURATION_FUTURE
        if self.timer >= total_duration:
            self._finish_splash()

    def _finish_splash(self) -> None:
        if self.is_done:
            return
        self.is_done = True
        self.state_machine.pop()
        self.state_machine.push(TitleState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        bg_surf = self._future_bg if self.phase == "future" else self._past_bg
        surface.blit(bg_surf, (0, 0))

        if self._logo_surf:
            surface.blit(self._logo_surf, self._logo_pos)

        if self.flash_alpha > 0.0:
            self._flash_surf.fill((225, 60, 60, int(self.flash_alpha)))
            surface.blit(self._flash_surf, (0, 0))
