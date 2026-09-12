"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState


class AttackState(EntityBaseState):

    def enter(self) -> None:
        self.action = self.entity.get_action("attack")
        is_up = self.entity.is_looking_up
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

        self.entity.attack_requested = False
        self.entity.swing_id = getattr(self.entity, "swing_id", 0) + 1

    def update(self, dt: float) -> None:
        if self.entity.attack_requested and not self.in_combo_followup:
            self.combo_buffered = True
            self.entity.attack_requested = False

        self.apply_horizontal_movement()

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
                    self.entity.swing_id = getattr(self.entity, "swing_id", 0) + 1
                else:
                    is_done = True

        if anim and anim.times_played > 0:
            is_done = True

        if is_done:
            if self.action.get("on_finish"):
                self.action["on_finish"](self.entity)

            if not self.entity.on_ground:
                self.change_state("fall")
            elif self.entity.vx != 0.0:
                self.change_state("walk")
            else:
                self.change_state("idle")

    def exit(self) -> None:
        if hasattr(self, "action") and self.action.get("on_finish"):
            self.action["on_finish"](self.entity)
