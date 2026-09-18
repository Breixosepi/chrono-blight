"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState
import settings

class DeathState(EntityBaseState):
    def enter(self) -> None:
        settings.SOUNDS["player-death"].play()
        if "lava" in settings.SOUNDS:
            settings.SOUNDS["lava"].stop()
        if "lava-shower" in settings.SOUNDS:
            settings.SOUNDS["lava-shower"].stop()
        if "saw-hazard" in settings.SOUNDS:
            settings.SOUNDS["saw-hazard"].stop()
        player = self.entity
        player.change_animation("death")
        player.vx = 0.0

    def update(self, dt: float) -> None:
        player = self.entity
        player.vx = 0.0
        
        if player.is_animation_finished():
            if player.skin in player.available_skins:
                player.available_skins.remove(player.skin)
                
            if player.available_skins:
                next_skin = player.available_skins[0]
                player.change_skin(next_skin)
                player.health = player.MAX_HEALTH
                self.change_state("idle")
