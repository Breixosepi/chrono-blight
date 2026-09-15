"""
Chrono Blight — BossBaseState
Estado base del que heredan todos los estados de boss.
Espeja EntityBaseState pero con referencia tipada a Boss.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from gale.state import BaseState

if TYPE_CHECKING:
    from src.entities.Boss import Boss
    from gale.state import StateMachine


class BossBaseState(BaseState):
    """Estado base para todos los estados del jefe."""

    def __init__(self, entity: "Boss", state_machine: "StateMachine") -> None:
        super().__init__(state_machine)
        self.entity = entity
        self.state_machine = state_machine
        self.has_gravity: bool = True

    def change_state(self, name: str, *args, **kwargs) -> None:
        self.entity.change_state(name, *args, **kwargs)

    def is_player_alive(self) -> bool:
        p = self.entity.player
        return p is not None and not p.is_dead()

