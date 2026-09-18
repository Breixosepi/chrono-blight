"""
Chrono Blight - HarvesterWalkState
Walks towards player and transitions to appropriate attacks.
"""
import random
from typing import TYPE_CHECKING
from src.states.entity.boss.BossBaseState import BossBaseState

if TYPE_CHECKING:
    from src.entities.Boss import Boss


class HarvesterWalkState(BossBaseState):
    def __init__(self, entity: "Boss", sm):
        super().__init__(entity, sm)
        self.entity = entity
        self.walk_timer: float = 0.0
        self.max_walk_time: float = 2.2

    def enter(self) -> None:
        self.entity.change_animation("walk")
        self.entity.can_hit_player = True
        self.walk_timer = 0.0

        phase = getattr(self.entity, "boss_phase", 1)
        self.max_walk_time = random.uniform(1.2, 2.2) if phase != 3 else random.uniform(0.6, 1.2)

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.entity.room is None or self.entity.room.player is None:
            return

        if self.entity.health <= 0:
            self.entity.change_state("death")
            return

        player = self.entity.room.player
        dx = player.hitbox.centerx - self.entity.hitbox.centerx
        dist = abs(dx)

        speed = self.entity.walk_speed * (1.35 if getattr(self.entity, "boss_phase", 1) == 3 else 1.0)
        if dx < -10:
            self.entity.facing = "left"
            self.entity.vx = -speed
        elif dx > 10:
            self.entity.facing = "right"
            self.entity.vx = speed
        else:
            self.entity.vx = 0.0

        self.walk_timer += dt

        if dist <= 75:
            self.entity.vx = 0.0
            self.entity.change_state("attack")
            return

        if getattr(self.entity, "boss_phase", 1) == 3:
            if dist > 140:
                self.entity.vx = 0.0
                self.entity.change_state("dash")
                return
            elif self.walk_timer > 0.5:
                self.entity.vx = 0.0
                self.entity.change_state("attack")
                return

        if self.walk_timer >= self.max_walk_time:
            self.entity.vx = 0.0
            self.entity.change_state("attack")
