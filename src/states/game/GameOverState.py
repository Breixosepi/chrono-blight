"""
Chrono Blight - Game Over State
"""

from typing import Any
import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings


class GameOverState(BaseState):

    def enter(self, **params: Any) -> None:
        self.overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill((25, 5, 5, 200))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "enter" and input_data.pressed:
            from src.states.game.TitleState import TitleState

            while len(self.state_machine.states) > 0:
                self.state_machine.pop()
            self.state_machine.push(TitleState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.overlay, (0, 0))

        render_text(
            surface,
            "GAME OVER",
            settings.FONTS["title"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 - 16,
            (230, 45, 45),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "Presiona ENTER para volver al inicio",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 + 16,
            (240, 240, 240),
            center=True,
            shadowed=True,
        )

