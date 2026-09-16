"""
Chrono Blight - LurkerIdleState
"""
import random
from src.states.entity.boss.BossBaseState import BossBaseState


class LurkerIdleState(BossBaseState):
    def enter(self, cooldown: float = 2.0, *args, **kwargs) -> None:
        boss = self.entity
        boss.vx = 0.0
        boss.vy = 0.0
        self.cooldown = cooldown
        boss.change_animation("idle")

    def update(self, dt: float) -> None:
        boss = self.entity
        boss.vx = 0.0
        boss.vy = 0.0

        if boss.player is not None:
            direction = boss.player_direction()
            boss.facing = "right" if direction > 0 else "left"

        self.cooldown -= dt
        if self.cooldown <= 0:
            if self.is_player_alive() and getattr(boss, "is_active", lambda: True)():
                self.change_state("attack")
            else:
                self.cooldown = 1.0

