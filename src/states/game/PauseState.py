"""
Chrono Blight - Pause State
"""
from typing import Any
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings


class PauseState(BaseState):
    def enter(self, **params: Any) -> None:
        self.overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill((0, 0, 0, 180))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.overlay, (0, 0))
        
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