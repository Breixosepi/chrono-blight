from typing import Any
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs

class PlayerIdleState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation("idle")
        self.entity.vx = 0.0

    def update(self, dt: float) -> None:
        commands = self.entity.commands
        if commands:
            if commands.move_right and not commands.move_left:
                self.entity.facing = "right"
            elif commands.move_left and not commands.move_right:
                self.entity.facing = "left"

            if commands.dash and self.entity.can_dash():
                self.change_state("dash")
                return
            elif commands.attack and self.entity.can_attack():
                self.change_state("attack")
                return
            elif commands.attack_special and self.entity.can_special_attack():
                self.change_state("attack_special")
                return
            elif commands.jump and self.entity.jumps_left > 0:
                self.change_state("airborne", jumping=True)
                return
            elif commands.move_left or commands.move_right:
                self.change_state("walk")
                return

        if not self.entity.on_ground:
            self.change_state("airborne")
            return

        self.entity._tick_anim(dt)
        self.entity._apply_physics(dt)

