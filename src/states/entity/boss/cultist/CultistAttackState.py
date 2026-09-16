"""
Chrono Blight - CultistAttackState
"""
from src.states.entity.boss.BossBaseState import BossBaseState


class CultistAttackState(BossBaseState):
    def enter(self, *args, **kwargs) -> None:
        boss = self.entity
        self.attack_timer: float = 0.0
        boss.vx = 0.0

        if boss.player is not None:
            direction = boss.player_direction()
            boss.facing = "right" if direction > 0 else "left"

        boss.change_animation("attack")
        self._spawn_phase_attack()

    def update(self, dt: float) -> None:
        boss = self.entity
        self.attack_timer += dt

        if self.attack_timer < 0.2 and boss.player is not None:
            direction = boss.player_direction()
            boss.facing = "right" if direction > 0 else "left"

        boss.vx = 0.0

        if boss.is_animation_finished(fallback_duration=boss.attack_duration):
            if self.is_player_alive() and boss.distance_to_player() <= boss.detect_range:
                current_phase = getattr(boss, "boss_phase", 1)
                cooldown_penalty = 0.0 if current_phase == 1 else 3.0
                final_cooldown = boss.attack_cooldown + cooldown_penalty
                
                self.change_state("chase", cooldown=final_cooldown)
            else:
                self.change_state("patrol")

    def _spawn_phase_attack(self) -> None:
        boss = self.entity
        if boss.player is None:
            return

        direction = 1.0 if boss.facing == "right" else -1.0
        base_y = float(boss.hitbox.bottom)
        spawn_x = float(boss.hitbox.right if direction > 0 else boss.hitbox.left)
        
        target_x = float(boss.player.hitbox.centerx)
        target_y = float(boss.player.hitbox.centery)
        current_phase = getattr(boss, "boss_phase", 1)

        if current_phase == 1:
            boss.spawn_ground_shockwave(spawn_x, base_y + 16.0, direction, speed=165.0, damage=14)
        elif current_phase == 2:
            boss.spawn_void_orb(spawn_x, base_y - 24.0, target_x, target_y, speed=85.0, damage=16)
        else:
            boss.spawn_ground_shockwave(spawn_x, base_y + 16.0, direction, speed=170.0, damage=15)
            boss.spawn_void_orb(spawn_x, base_y - 24.0, target_x, target_y, speed=90.0, damage=16)