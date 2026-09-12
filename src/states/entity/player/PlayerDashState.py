from typing import Any
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs

class PlayerDashState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation("dash")
        action = self.entity.get_action("dash")
        self.dash_speed = action.get("dash_speed", 220.0)
        cost = action.get("mana_cost", 0)
        if cost > 0:
            self.entity.consume_mana(cost)
        if action.get("func"):
            action["func"](self.entity)

    def update(self, dt: float) -> None:
        self.entity._tick_anim(dt)
        self.entity.vx = self.dash_speed if self.entity.facing == "right" else -self.dash_speed
        
        anim_frames = self.entity._get_anim_dict().get("dash", [0])
        anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
            "dash", {"interval": 1/10.0}
        )
        duration = len(anim_frames) * anim_def["interval"]
        
        is_done = (
            (self.entity.current_animation and self.entity.current_animation.times_played > 0)
            or self.entity._anim_timer >= duration
        )
        
        if is_done:
            self.entity.vx = 0.0
            if not self.entity.on_ground:
                self.change_state("airborne")
            else:
                self.change_state("idle")
            return
        
        self.entity._apply_physics(dt)

