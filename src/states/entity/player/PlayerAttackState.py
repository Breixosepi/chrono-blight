from typing import Any
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs

class PlayerAttackState(EntityBaseState):
    def enter(self) -> None:
        self.action = self.entity.get_action("attack")
        commands = self.entity.commands
        is_up = bool(commands and commands.up)
        up_anim = self.action.get("up_anim")

        if is_up and up_anim:
            self.entity.change_animation(up_anim)
            self.in_combo_followup = True
            self.combo_buffered = False
            self.current_anim_name = up_anim
        else:
            self.entity.change_animation("attack")
            self.in_combo_followup = False
            self.combo_buffered = False
            self.current_anim_name = "attack"

        cost = self.action.get("mana_cost", 0)
        if cost > 0:
            self.entity.consume_mana(cost)
        if self.action.get("on_start"):
            self.action["on_start"](self.entity)

    def update(self, dt: float) -> None:
        commands = self.entity.commands
        if commands:
            if commands.attack and not self.in_combo_followup:
                self.combo_buffered = True

            if commands.move_right and not commands.move_left:
                self.entity.facing = "right"
                self.entity.vx = entity_defs.RUN_SPEED if commands.run else entity_defs.WALK_SPEED
            elif commands.move_left and not commands.move_right:
                self.entity.facing = "left"
                self.entity.vx = -(entity_defs.RUN_SPEED if commands.run else entity_defs.WALK_SPEED)
            else:
                self.entity.vx = 0.0
        else:
            self.entity.vx = 0.0

        self.entity._tick_anim(dt)
        if self.action.get("on_update"):
            self.action["on_update"](self.entity, dt)
        
        anim = self.entity.current_animation
        curr_idx = anim.current_frame_index if anim else 0
        combo_def = self.action.get("combo")

        is_done = False

        if combo_def and not self.in_combo_followup and self.current_anim_name == "attack":
            hit1_limit = combo_def.get("hit1_frames", 7)
            if curr_idx >= hit1_limit:
                if self.combo_buffered:
                    self.in_combo_followup = True
                else:
                    is_done = True

        if anim and anim.times_played > 0:
            is_done = True

        if is_done:
            if self.action.get("on_finish"):
                self.action["on_finish"](self.entity)

            if not self.entity.on_ground:
                self.change_state("airborne")
            elif self.entity.vx != 0.0:
                self.change_state("walk")
            else:
                self.change_state("idle")
            return
        
        self.entity._apply_physics(dt)

