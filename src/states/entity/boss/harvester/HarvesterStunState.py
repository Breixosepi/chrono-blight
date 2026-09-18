"""
Chrono Blight - HarvesterStunState
The Harvester is stunned after all 3 monoliths are activated, leaving it vulnerable.
"""
from typing import TYPE_CHECKING
from src.states.entity.boss.BossBaseState import BossBaseState

if TYPE_CHECKING:
    from src.entities.Boss import Boss


class HarvesterStunState(BossBaseState):
    def __init__(self, entity: "Boss", sm):
        super().__init__(entity, sm)
        self.entity = entity
        self.stun_timer: float = 0.0
        self.max_duration: float = 5.5

    def enter(self, duration: float = 5.5) -> None:
        self.max_duration = duration
        self.stun_timer = 0.0
        self.entity.vx = 0.0
        self.entity.can_hit_player = False
        self.entity.invulnerable = False
        self.entity.shield_active = False
        self.entity.change_animation("startup")

        if self.entity.room:
            self.entity.room.camera.shake(4.0, 0.35)
            self.entity.room._spawn_popup("¡ATURDIDO!", self.entity.hitbox.centerx, self.entity.hitbox.top - 14, 1.2, (255, 230, 80))

    def update(self, dt: float) -> None:
        if self.entity.health <= 0:
            self.entity.change_state("death")
            return

        self.stun_timer += dt
        self.entity.vx = 0.0

        # Loop or hold the startup frame
        anim = self.entity.current_animation
        if anim and anim.times_played > 0:
            anim.current_frame_index = len(anim.frames) - 1

        if self.stun_timer >= self.max_duration:
            self.entity.can_hit_player = True
            if self.entity.room:
                self.entity.room.camera.shake(3.0, 0.2)
                self.entity.room.spawn_dust(self.entity.hitbox.centerx, self.entity.hitbox.bottom, count=12)
            self.entity.change_state("idle")

