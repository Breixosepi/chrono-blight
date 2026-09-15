"""
Chrono Blight — BossChaseState
El jefe cultista es un lanzador de conjuros estático: permanece en su esquina
mirando al jugador y pasa al ataque cuando el cooldown expire.
"""
from src.states.entity.boss.BossBaseState import BossBaseState


class BossChaseState(BossBaseState):
    def enter(self, *args, **kwargs) -> None:
        e = self.entity
        self.has_gravity = True
        self.attack_cooldown: float = kwargs.get("cooldown", 0.0)
        e.vx = 0.0
        e.change_animation("idle")

    def update(self, dt: float) -> None:
        e = self.entity

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if not self.is_player_alive():
            return

        # Siempre mira al jugador aunque no se mueva
        direction = e.player_direction()
        e.facing = "right" if direction > 0 else "left"

        e.vx = 0.0

        if self.attack_cooldown <= 0:
            self.change_state("attack")

