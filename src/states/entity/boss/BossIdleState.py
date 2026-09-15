"""
Chrono Blight — BossIdleState
El jefe está quieto, esperando o en transición entre fases (invulnerable).
"""
from src.states.entity.boss.BossBaseState import BossBaseState


class BossIdleState(BossBaseState):
    def enter(self, *args, **kwargs) -> None:
        e = self.entity
        self.has_gravity = True
        e.vx = 0.0
        e.change_animation("idle")

    def update(self, dt: float) -> None:
        # El BossIdleState es pasivo; la ArenaManager controla la transición de vuelta a chase/attack.
        self.entity.vx = 0.0

