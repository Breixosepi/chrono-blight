"""
Chrono Blight - Play State
"""

from typing import Any
import pygame

from gale.state import BaseState
from gale.input_handler import InputData

from src.world.Room import Room
from src.ui.HUD import HUD
from src.states.game.PauseState import PauseState
from src.states.game.PhaseShiftState import PhaseShiftState
from src.states.game.GameOverState import GameOverState


class PlayState(BaseState):

    def enter(self, **params: Any) -> None:
        self.room = Room()
        self.player = self.room.player
        self.hud = HUD()

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        if self.player.is_dead() and self.player.is_animation_finished():
            self.state_machine.push(GameOverState(self.state_machine))
            return

        self.room.update(dt)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.push(PauseState(self.state_machine))

        elif input_id == "phase_shift" and input_data.pressed:
            if self.player.toggle_phase():
                self.state_machine.push(
                    PhaseShiftState(self.state_machine), phase_color=self.player.phase_color
                )

        elif input_id == "prev_form" and input_data.pressed:
            self.player.cycle_skin(-1)

        elif input_id in ("next_form", "toggle_morph") and input_data.pressed:
            self.player.cycle_skin(1)

        else:
            self.player.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.room.render(surface)

        cam_x, cam_y = self.room.camera_offset
        self.hud.render(surface, self.player, cam_x, cam_y)
