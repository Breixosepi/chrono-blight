from typing import Any
import pygame

from gale.state import BaseState
from gale.input_handler import InputData


class PauseState(BaseState):

    def enter(self, **params: Any) -> None:
        pass

    def on_input(self, input_id: str, input_data: InputData) -> None:

        if input_id == "pause" and input_data.pressed:
            self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 48)
        text = font.render("PAUSED - Press P to Resume", True, (255, 200, 0))
        surface.blit(text, (surface.get_width() // 2 - 200, surface.get_height() // 2))

