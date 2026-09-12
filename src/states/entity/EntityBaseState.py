"""
Chrono Blight
"""

from typing import Any
import pygame
from gale.state import BaseState, StateMachine


class EntityBaseState(BaseState):
    has_gravity: bool = True

    def __init__(self, entity: Any, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.entity = entity

    def change_state(self, state_name: str, *args: Any, **kwargs: Any) -> None:
        if hasattr(self.entity, "change_state"):
            self.entity.change_state(state_name, *args, **kwargs)
        else:
            self.state_machine.change(state_name, *args, **kwargs)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface, camera_x: float = 0.0, camera_y: float = 0.0) -> None:
        pass
