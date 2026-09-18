"""
Chrono Blight - HarvesterIdleState
Idle state with phase color cycling for Phase 1 and combat decision making.
"""
import random
from typing import TYPE_CHECKING
from gale.timer import Timer

from src.states.entity.boss.BossBaseState import BossBaseState
import settings

if TYPE_CHECKING:
    from src.entities.Boss import Boss


class HarvesterIdleState(BossBaseState):
    def __init__(self, entity: "Boss", sm):
        super().__init__(entity, sm)
        self.entity = entity
        self.wait_timer: float = 0.0
        self.max_wait: float = 1.5
        self.phase_shift_timer: float = 0.0

    def enter(self, cooldown: float = 1.2) -> None:
        self.entity.change_animation("idle")
        self.entity.can_hit_player = True
        self.entity.vx = 0.0
        self.wait_timer = 0.0

        phase = getattr(self.entity, "boss_phase", 1)
        if phase == 3:
            self.max_wait = random.uniform(0.5, 0.9)
        elif phase == 2:
            self.max_wait = random.uniform(0.65, 1.0)
        else:
            self.max_wait = cooldown

        self.entity.phase = "neutral"

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.entity.room is None or self.entity.room.player is None:
            return

        if self.entity.health <= 0:
            self.entity.change_state("death")
            return

        player = self.entity.room.player

        if player.hitbox.centerx < self.entity.hitbox.centerx:
            self.entity.facing = "left"
        else:
            self.entity.facing = "right"

        self.wait_timer += dt
        if self.wait_timer >= self.max_wait:
            dist = abs(self.entity.hitbox.centerx - player.hitbox.centerx)
            phase = getattr(self.entity, "boss_phase", 1)

            if phase == 3:
                self.entity.change_state("attack")
            elif phase == 2:
                if dist < 80:
                    self.entity.change_state("attack")
                elif random.random() < 0.40:
                    self.entity.change_state("walk")
                else:
                    self.entity.change_state("attack")
            else:
                if dist < 80:
                    self.entity.change_state("attack")
                elif random.random() < 0.60:
                    self.entity.change_state("walk")
                else:
                    self.entity.change_state("attack")
