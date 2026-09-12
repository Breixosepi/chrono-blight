"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState


class DeathState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("death")
        self.entity.vx = 0.0

    def update(self, dt: float) -> None:
        self.entity.vx = 0.0

        if self.entity.is_animation_finished():
            if self.entity.skin in self.entity.available_skins:
                self.entity.available_skins.remove(self.entity.skin)

            if self.entity.available_skins:
                next_skin = self.entity.available_skins[0]
                self.entity.change_skin(next_skin)
                self.entity.health = self.entity.MAX_HEALTH
                self.change_state("idle")

