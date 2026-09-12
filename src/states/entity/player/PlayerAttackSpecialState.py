from typing import Any
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs

class PlayerAttackSpecialState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation("attack_special")
        self.entity.vx = 0.0
        self.action = self.entity.get_action("special")
        cost = self.action.get("mana_cost", 0)
        if cost > 0:
            self.entity.consume_mana(cost)
        if self.action.get("on_start"):
            self.action["on_start"](self.entity)

    def update(self, dt: float) -> None:
        self.entity._tick_anim(dt)
        self.entity.vx = 0.0

        if self.action.get("on_update"):
            self.action["on_update"](self.entity, dt)

        if "duration" in self.action:
            duration = self.action["duration"]
            is_done = self.entity._anim_timer >= duration
        else:
            anim_frames = self.entity._get_anim_dict().get("attack_special", [0])
            anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
                "attack_special", {"interval": 1/10.0}
            )
            duration = len(anim_frames) * anim_def["interval"]
            is_done = (
                (self.entity.current_animation and self.entity.current_animation.times_played > 0)
                or self.entity._anim_timer >= duration
            )

        if is_done:
            if self.action.get("on_finish"):
                self.action["on_finish"](self.entity)
            
            if not self.entity.on_ground:
                self.change_state("airborne")
            else:
                self.change_state("idle")
            return
        
        self.entity._apply_physics(dt)

