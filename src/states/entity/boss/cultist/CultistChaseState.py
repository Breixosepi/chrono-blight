"""
Chrono Blight - CultistChaseState
"""
from src.states.entity.boss.BossBaseState import BossBaseState


class CultistChaseState(BossBaseState):
    def enter(self, *args, **kwargs) -> None:
        boss = self.entity
        self.attack_cooldown: float = kwargs.get("cooldown", 0.0)
        boss.vx = 0.0
        boss.change_animation("idle")

    def update(self, dt: float) -> None:
        boss = self.entity

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if not self.is_player_alive():
            return

        direction = boss.player_direction()
        boss.facing = "right" if direction > 0 else "left"
        boss.vx = 0.0

        if self.attack_cooldown <= 0:
            self.change_state("attack")