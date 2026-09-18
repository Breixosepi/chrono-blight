"""
Chrono Blight - HarvesterDashState
Fast phantom dash across the room for Phase 3.
"""
from typing import TYPE_CHECKING
import pygame
from src.states.entity.boss.BossBaseState import BossBaseState
import settings

if TYPE_CHECKING:
    from src.entities.Boss import Boss


class HarvesterDashState(BossBaseState):
    def __init__(self, entity: "Boss", sm):
        super().__init__(entity, sm)
        self.entity = entity
        self.dash_timer: float = 0.0
        self.dash_duration: float = 0.45
        self.dash_speed: float = 320.0
        self.hit_done: bool = False

    def enter(self) -> None:
        self.dash_timer = 0.0
        self.hit_done = False
        self.entity.can_hit_player = True

        # Face and dash towards player
        player = self.entity.room.player if self.entity.room else None
        if player:
            if player.hitbox.centerx < self.entity.hitbox.centerx:
                self.entity.facing = "left"
                self.entity.vx = -self.dash_speed
            else:
                self.entity.facing = "right"
                self.entity.vx = self.dash_speed
        else:
            self.entity.vx = -self.dash_speed if self.entity.facing == "left" else self.dash_speed

        self.entity.change_animation("walk")
        if "sword" in settings.SOUNDS:
            settings.SOUNDS["sword"].play()
        if self.entity.room:
            self.entity.room.spawn_dust(self.entity.hitbox.centerx, self.entity.hitbox.bottom, count=10)

    def update(self, dt: float) -> None:
        if self.entity.health <= 0:
            self.entity.change_state("death")
            return

        self.dash_timer += dt

        # Spawn ghost afterimages in the room
        if self.entity.room and int(self.dash_timer * 60) % 4 == 0:
            self.entity.room.spawn_dust(self.entity.hitbox.centerx, self.entity.hitbox.bottom, count=3)

        # Check contact damage during dash
        player = self.entity.room.player if self.entity.room else None
        if player and not player.is_dead() and not self.hit_done:
            is_sword_special = (player.state_name == "attack_special" and player.skin == "sword")
            if (
                player.state_name not in ("hit", "death", "dash")
                and not is_sword_special
                and player.invulnerable_timer <= 0.0
                and self.entity.hitbox.colliderect(player.hitbox)
            ):
                self.hit_done = True
                player.take_damage(16, source_x=self.entity.hitbox.centerx)
                if self.entity.room:
                    self.entity.room.camera.shake(4.0, 0.2)
                    self.entity.room._spawn_popup("-16 (DASH)", player.hitbox.centerx, player.hitbox.top - 10, 0.7, (255, 75, 75))
                    self.entity.room.spawn_dust(player.hitbox.centerx, player.hitbox.bottom, count=8)

        if self.dash_timer >= self.dash_duration:
            self.entity.vx = 0.0
            # Follow up with immediate attack or dimensional slash
            self.entity.change_state("attack")

