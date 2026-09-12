from typing import Any
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs

class PlayerDeathState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation("death")
        self.entity.vx = 0.0

    def update(self, dt: float) -> None:
        self.entity.vx = 0.0
        self.entity._tick_anim(dt)
        self.entity._apply_physics(dt)

        anim_frames = self.entity._get_anim_dict().get("death", [0])
        anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
            "death", {"interval": 1/7.0}
        )
        duration = len(anim_frames) * anim_def["interval"]

        is_done = (
            (self.entity.current_animation and self.entity.current_animation.times_played > 0)
            or self.entity._anim_timer >= duration
        )

        if is_done:
            if self.entity.skin in self.entity.available_skins:
                self.entity.available_skins.remove(self.entity.skin)

            if self.entity.available_skins:
                next_skin = self.entity.available_skins[0]
                self.entity.change_skin(next_skin)
                self.entity.health = self.entity.MAX_HEALTH  # Restaura la vida para la nueva forma
                self.change_state("idle")

