"""
Chrono Blight - Splash Screen State
"""
from typing import Any
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer

import settings
from src.states.game.TitleState import TitleState


class SplashState(BaseState):
    DURATION_PAST: float = 1.0 
    DURATION_FUTURE: float = 1.0  

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
        self._fade_surf = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )

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
        surface.fill((10, 8, 14))

        tex_key = "logo_future" if self.phase == "future" else "logo_past"
        logo_tex = settings.TEXTURES.get(tex_key)
        if logo_tex:
            surface.blit(logo_tex, (0, 0))

        if self.flash_alpha > 0.0:
            self._flash_surf.fill((220, 60, 60, int(self.flash_alpha)))
            surface.blit(self._flash_surf, (0, 0))

