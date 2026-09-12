"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState


class EnemyBaseState(EntityBaseState):
    has_gravity: bool = True

    def is_player_alive(self) -> bool:
        p = self.entity.player
        if p is None:
            return False
        if hasattr(p, "is_dead") and p.is_dead():
            return False
        if getattr(p, "state_name", "") == "death":
            return False
        return True

