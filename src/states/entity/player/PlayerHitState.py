from typing import Any
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs

class PlayerHitState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation("hit")
        self.entity.vx = 0.0

    def update(self, dt: float) -> None:
        self.entity._tick_anim(dt)
        self.entity.vx = 0.0
        
        anim_frames = self.entity._get_anim_dict().get("hit", [0])
        anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
            "hit", {"interval": 1/6.0}
        )
        duration = len(anim_frames) * anim_def["interval"]
        
        is_done = (
            (self.entity.current_animation and self.entity.current_animation.times_played > 0)
            or self.entity._anim_timer >= duration
        )
        
        if is_done:
            self.change_state("idle")
            return
            
        self.entity._apply_physics(dt)

