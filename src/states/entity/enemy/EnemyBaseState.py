"""
Chrono Blight - EnemyBaseState
"""
from src.states.entity.EntityBaseState import EntityBaseState

class EnemyBaseState(EntityBaseState):
    has_gravity: bool = True

    def is_player_alive(self) -> bool:
        player = self.entity.player
        if player is None:
            return False
        if hasattr(player, "is_dead") and player.is_dead():
            return False
        if getattr(player, "state_name", "") == "death":
            return False
        return True