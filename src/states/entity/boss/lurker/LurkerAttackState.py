"""
Chrono Blight - LurkerAttackState
"""
import random
from src.states.entity.boss.BossBaseState import BossBaseState


class LurkerAttackState(BossBaseState):
    def enter(self, *args, **kwargs) -> None:
        boss = self.entity
        self.attack_timer: float = 0.0
        boss.vx = 0.0
        boss.vy = 0.0

        if boss.player is not None:
            direction = boss.player_direction()
            boss.facing = "right" if direction > 0 else "left"

        boss.change_animation("attack")
        self._spawn_phase_attack()

    def update(self, dt: float) -> None:
        boss = self.entity
        self.attack_timer += dt
        boss.vx = 0.0
        boss.vy = 0.0

        if boss.is_animation_finished(fallback_duration=boss.attack_duration):
            phase = getattr(boss, "boss_phase", 1)
            next_cd = 2.4 if phase == 1 else (2.0 if phase == 2 else 1.6)
            self.change_state("idle", cooldown=next_cd)

    def _spawn_phase_attack(self) -> None:
        boss = self.entity
        if boss.player is None:
            return

        phase = getattr(boss, "boss_phase", 1)
        px = boss.player.hitbox.centerx
        py = boss.player.hitbox.centery

        if phase == 1:
            boss.spawn_burst(px, py)
        elif phase == 2:
            direction = random.choice([1.0, -1.0])
            start_x = -60.0 if direction > 0 else boss.map_w + 60.0
            boss.spawn_side_shoot(py, direction, start_x)
        else:
            boss.spawn_burst(px, py)
            direction = random.choice([1.0, -1.0])
            start_x = -60.0 if direction > 0 else boss.map_w + 60.0
            boss.spawn_side_shoot(py, direction, start_x)

