"""
Chrono Blight
"""

from typing import Any
import pygame
from gale.state import BaseState, StateMachine


from src.definitions import entity as entity_defs


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

    def apply_horizontal_movement(self) -> None:
        e = self.entity
        if e.move_direction != 0:
            e.facing = "left" if e.move_direction < 0 else "right"
            speed = entity_defs.RUN_SPEED if getattr(e, "is_running", False) else entity_defs.WALK_SPEED
            e.vx = speed * e.move_direction
        else:
            e.vx = 0.0

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface, camera_x: float = 0.0, camera_y: float = 0.0) -> None:
        pass
