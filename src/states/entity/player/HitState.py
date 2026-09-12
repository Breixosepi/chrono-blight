"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs


class HitState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("hit")
        self.entity.vx = 0.0

        anim_frames = self.entity._get_anim_dict().get("hit", [0])
        anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
            "hit", {"interval": 1/6.0}
        )
        self.duration = len(anim_frames) * anim_def["interval"]

    def update(self, dt: float) -> None:
        self.entity.vx = 0.0

        if self.entity.is_animation_finished(fallback_duration=self.duration):
            if self.entity.on_ground:
                self.change_state("idle")
            else:
                self.change_state("fall")

