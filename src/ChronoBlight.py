import pygame
from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateStack
import settings
from src.states.game.TitleState import TitleState
from src.states.game.SplashState import SplashState


class ChronoBlight(Game):

    def init(self) -> None:
        for key in settings.TEXTURES:
            settings.TEXTURES[key] = settings.TEXTURES[key].convert_alpha()

        self.state_stack = StateStack()
        self.state_stack.push(SplashState(self.state_stack))
        
    def reset_to_title(self) -> None:
        settings.stop_all_music()
        while len(self.state_stack.states) > 0:
            self.state_stack.pop()
        self.state_stack.push(TitleState(self.state_stack))

    def update(self, dt: float) -> None:
        self.state_stack.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_stack.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.state_stack.on_input(input_id, input_data)
