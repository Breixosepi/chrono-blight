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

        # Shorter idle in Phase 3
        if getattr(self.entity, "boss_phase", 1) == 3:
            self.max_wait = random.uniform(0.5, 0.9)
        else:
            self.max_wait = cooldown

        # Ensure Phase 1 has a phase color
        if getattr(self.entity, "boss_phase", 1) == 1 and self.entity.phase not in ("green", "red"):
            self.entity.phase = "green"

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.entity.room is None or self.entity.room.player is None:
            return

        if self.entity.health <= 0:
            self.entity.change_state("death")
            return

        player = self.entity.room.player

        # Face player
        if player.hitbox.centerx < self.entity.hitbox.centerx:
            self.entity.facing = "left"
        else:
            self.entity.facing = "right"

        # Phase 1: Periodic phase shift (Green <-> Red)
        if getattr(self.entity, "boss_phase", 1) == 1:
            self.phase_shift_timer += dt
            if self.phase_shift_timer >= 6.5:
                self.phase_shift_timer = 0.0
                new_phase = "red" if self.entity.phase == "green" else "green"
                self.entity.phase = new_phase
                if self.entity.room:
                    sfx = "phase_shift_future" if new_phase == "red" else "phase_shift_past"
                    if sfx in settings.SOUNDS:
                        settings.SOUNDS[sfx].play()
                    txt = "FUTURO (ROJO)" if new_phase == "red" else "PASADO (VERDE)"
                    col = (255, 90, 90) if new_phase == "red" else (90, 240, 150)
                    self.entity.room._spawn_popup(txt, self.entity.hitbox.centerx, self.entity.hitbox.top - 12, 0.9, col)
                    self.entity.room.camera.shake(2.0, 0.15)
                    self.entity.room.spawn_dust(self.entity.hitbox.centerx, self.entity.hitbox.bottom, count=10)

        self.wait_timer += dt
        if self.wait_timer >= self.max_wait:
            dist = abs(self.entity.hitbox.centerx - player.hitbox.centerx)
            phase = getattr(self.entity, "boss_phase", 1)

            if phase == 3:
                # En fase 3: El jefe aguarda en su plataforma percha bombardeando
                # con cortes aéreos y cortes dimensionales mientras el jugador hace parkour.
                # Solo se teletransporta cuando el jugador llega y le conecta un golpe.
                self.entity.change_state("attack")
            else:
                if dist < 80:
                    self.entity.change_state("attack")
                elif random.random() < 0.60:
                    self.entity.change_state("walk")
                else:
                    self.entity.change_state("attack")
