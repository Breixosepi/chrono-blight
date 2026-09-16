"""
Chrono Blight - BossIdleState
"""
from src.states.entity.boss.BossBaseState import BossBaseState


class BossIdleState(BossBaseState):
    def enter(self, *args, **kwargs) -> None:
        boss = self.entity
        boss.vx = 0.0
        boss.change_animation("idle")

    def update(self, dt: float) -> None:
        self.entity.vx = 0.0