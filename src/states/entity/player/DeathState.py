"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs


class DeathState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("death")
        self.entity.vx = 0.0

        anim_frames = self.entity._get_anim_dict().get("death", [0])
        anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
            "death", {"interval": 1/7.0}
        )
        self.duration = len(anim_frames) * anim_def["interval"]

    def update(self, dt: float) -> None:
        self.entity.vx = 0.0

        if self.entity.is_animation_finished(fallback_duration=self.duration):
            if self.entity.skin in self.entity.available_skins:
                self.entity.available_skins.remove(self.entity.skin)

            if self.entity.available_skins:
                next_skin = self.entity.available_skins[0]
                self.entity.change_skin(next_skin)
                self.entity.health = self.entity.MAX_HEALTH
                self.change_state("idle")

