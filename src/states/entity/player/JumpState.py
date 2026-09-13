"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs


class JumpState(EntityBaseState):

    def enter(self) -> None:
        if self.entity.on_ground and hasattr(self.entity, "on_jump_effect"):
            self.entity.on_jump_effect()
        self.entity.change_animation("jump")
        self.entity.vy = entity_defs.JUMP_VELOCITY
        self.entity.jumps_left -= 1
        self.entity.on_ground = False
        self.entity.jump_requested = False

    def update(self, dt: float) -> None:
        if not self.entity.jump_held and self.entity.vy < -120.0:
            self.entity.vy = -120.0

        self.apply_horizontal_movement()

        if self.entity.jump_requested and self.entity.jumps_left > 0:
            self.entity.jump_requested = False
            self.change_state("jump")
            return

        if self.entity.dash_requested:
            self.entity.dash_requested = False
            if self.entity.can_dash():
                self.change_state("dash")
                return
        elif self.entity.attack_requested:
            self.entity.attack_requested = False
            if self.entity.can_attack():
                self.change_state("attack")
                return
        elif self.entity.special_attack_requested:
            self.entity.special_attack_requested = False
            if self.entity.skin == "sword" and self.entity.can_special_attack():
                self.change_state("attack_special")
                return

        if self.entity.vy >= 0:
            self.change_state("fall")
            return

        if self.entity.on_ground:
            self.on_land()

    def on_land(self) -> None:
        self.change_state("walk" if self.entity.vx != 0.0 else "idle")
