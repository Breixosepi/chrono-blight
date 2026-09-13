"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState


class FallState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("fall")

    def update(self, dt: float) -> None:
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

        if self.entity.on_ground:
            self.on_land()

    def on_land(self) -> None:
        if self.entity.vx != 0.0:
            self.change_state("walk")
        else:
            self.change_state("idle")
