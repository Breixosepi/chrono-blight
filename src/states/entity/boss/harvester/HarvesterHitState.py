from typing import TYPE_CHECKING
import random
from src.states.entity.boss.BossBaseState import BossBaseState
import settings

if TYPE_CHECKING:
    from src.entities.Boss import Boss


class HarvesterHitState(BossBaseState):
    def __init__(self, entity: "Boss", sm):
        super().__init__(entity, sm)
        self.entity = entity
        self.timer: float = 0.0
        self.duration: float = 0.22

    def enter(self) -> None:
        self.timer = 0.0
        self.entity.change_animation("hit")
        self.entity.vx = 0.0

        if "enemy-hurt" in settings.SOUNDS:
            settings.SOUNDS["enemy-hurt"].play()

        player = self.entity.room.player if self.entity.room else None
        if player:
            if player.hitbox.centerx < self.entity.hitbox.centerx:
                self.entity.facing = "left"
            else:
                self.entity.facing = "right"

    def update(self, dt: float) -> None:
        if self.entity.health <= 0:
            self.entity.change_state("death")
            return

        self.timer += dt
        self.entity.vx = 0.0

        anim = self.entity.current_animation
        is_finished = (anim and anim.times_played > 0) or (self.timer >= self.duration)

        if is_finished:
            dist = self.entity.distance_to_player()
            if dist <= 85:
                self.entity.change_state("attack")
            elif getattr(self.entity, "boss_phase", 1) == 3 or random.random() < 0.35:
                self.entity.change_state("dash")
            else:
                self.entity.change_state("walk")

