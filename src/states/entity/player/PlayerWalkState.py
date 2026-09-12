from typing import Any
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs

class PlayerWalkState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation("walk")

    def update(self, dt: float) -> None:
        commands = self.entity.commands
        if commands:
            if commands.move_right and not commands.move_left:
                self.entity.facing = "right"
            elif commands.move_left and not commands.move_right:
                self.entity.facing = "left"

            if commands.move_left and not commands.move_right:
                self.entity.vx = -(entity_defs.RUN_SPEED if commands.run else entity_defs.WALK_SPEED)
            elif commands.move_right and not commands.move_left:
                self.entity.vx = entity_defs.RUN_SPEED if commands.run else entity_defs.WALK_SPEED
            else:
                self.entity.vx = 0.0

            target_anim = "run" if (commands.run and abs(self.entity.vx) > entity_defs.WALK_SPEED) else "walk"
            if getattr(self.entity, "_last_anim_name", None) != target_anim:
                self.entity.change_animation(target_anim)

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
            elif self.entity.vx == 0.0:
                self.change_state("idle")
                return

        if not self.entity.on_ground:
            self.change_state("airborne")
            return

        self.entity._tick_anim(dt)
        self.entity._apply_physics(dt)

