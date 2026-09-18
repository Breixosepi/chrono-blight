"""
Chrono Blight - AttackState
"""
from src.states.entity.EntityBaseState import EntityBaseState
import settings

class AttackState(EntityBaseState):
    def enter(self) -> None:

        player = self.entity
        self.action_def = player.get_action("attack")
        
        up_animation = self.action_def.get("up_anim")
        
        if player.is_looking_up and up_animation:
            player.change_animation(up_animation)
            self.in_combo_followup = True
            self.combo_buffered = False
            self.current_anim_name = up_animation
        else:
            player.change_animation("attack")
            self.in_combo_followup = False
            self.combo_buffered = False
            self.current_anim_name = "attack"

        mana_cost = self.action_def.get("mana_cost", 0)
        if mana_cost > 0:
            player.consume_mana(mana_cost)

        player.attack_requested = False
        player.swing_id = getattr(player, "swing_id", 0) + 1

        if player.skin == "sword":
            settings.SOUNDS["sword"].play()
        elif player.skin == "mage":
            settings.SOUNDS["mage-attack"].play()
        elif player.skin == "morph":
            settings.SOUNDS["morph-fire"].play()

    def update(self, dt: float) -> None:
        player = self.entity
        
        if player.attack_requested and not self.in_combo_followup:
            self.combo_buffered = True
            player.attack_requested = False
            
        self.apply_horizontal_movement()

        anim = player.current_animation
        current_frame_idx = anim.current_frame_index if anim else 0
        combo_definition = self.action_def.get("combo")
        
        is_attack_finished = False

        if combo_definition and not self.in_combo_followup and self.current_anim_name == "attack":
            hit1_limit_frame = combo_definition.get("hit1_frames", 7)
            if current_frame_idx >= hit1_limit_frame:
                if self.combo_buffered:
                    self.in_combo_followup = True
                    player.swing_id = getattr(player, "swing_id", 0) + 1
                    if player.skin == "sword":
                        settings.SOUNDS["sword"].play()
                else:
                    is_attack_finished = True

        if anim and anim.times_played > 0:
            is_attack_finished = True

        if is_attack_finished:
            if not player.on_ground:
                self.change_state("fall")
            elif player.vx != 0.0:
                self.change_state("walk")
            else:
                self.change_state("idle")