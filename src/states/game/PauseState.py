"""
Chrono Blight - Pause State
"""
from typing import Any, Optional
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings


class PauseState(BaseState):
    _OVERLAY: Optional[pygame.Surface] = None

    def enter(self, **params: Any) -> None:
        settings.pause_music("ambient")
        if PauseState._OVERLAY is None:
            PauseState._OVERLAY = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
            )
            PauseState._OVERLAY.fill((0, 0, 0, 180))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            settings.resume_music("ambient")
            self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        if PauseState._OVERLAY is not None:
            surface.blit(PauseState._OVERLAY, (0, 0))
        
        render_text(
            surface,
            "PAUSA",
            settings.FONTS["title"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 - 14,
            (255, 205, 50),
            center=True,
            shadowed=True,
        )
        
        render_text(
            surface,
            "Presiona P para reanudar",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 + 12,
            (240, 240, 240),
            center=True,
            shadowed=True,
        )