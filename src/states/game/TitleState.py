from typing import Any
import pygame

from gale.state import BaseState
from gale.input_handler import InputData


class TitleState(BaseState):

    def enter(self, **params: Any) -> None:
        pass

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "enter" and input_data.pressed:
            from src.states.game.PlayState import PlayState
            self.state_machine.pop()
            self.state_machine.push(PlayState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 10, 10))  
        font = pygame.font.Font(None, 36)
        text = font.render("TITLE STATE - Press Enter para jugar", True, (255, 255, 255))
        surface.blit(text, (20, 20))

