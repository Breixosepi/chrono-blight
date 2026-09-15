"""
Chrono Blight — BossAttackState
Maneja los ataques del Sumo Sacerdote Cultista según su fase activa.

Fase 1: Onda Rasante terrestre (esquivable saltando).
Fase 2: Orbe del Vacío flotante dirigido al jugador.
Fase 3: Combo — Onda Rasante + Orbe del Vacío simultáneos.
"""
import pygame
from src.states.entity.boss.BossBaseState import BossBaseState


class BossAttackState(BossBaseState):
    def enter(self, *args, **kwargs) -> None:
        e = self.entity
        self.has_gravity = True
        self._attack_timer: float = 0.0
        self._spell_launched: bool = False
        e.vx = 0.0

        # Girar hacia el jugador justo antes de lanzar
        if e.player is not None:
            direction = e.player_direction()
            e.facing = "right" if direction > 0 else "left"

        e.change_animation("attack")
        self._spawn_cultist_attack()

    def update(self, dt: float) -> None:
        e = self.entity
        self._attack_timer += dt

        # Mantener cara al jugador durante el wind-up
        if self._attack_timer < 0.2 and e.player is not None:
            direction = e.player_direction()
            e.facing = "right" if direction > 0 else "left"

        e.vx = 0.0

        if e.is_animation_finished(fallback_duration=e.attack_duration):
            if self.is_player_alive() and e.distance_to_player() <= e.detect_range:
                base_cd = getattr(e, "attack_cooldown", 2.4)
                phase = getattr(e, "boss_phase", 1)
                cd = base_cd if phase == 1 else (base_cd + 3.0)  # phase 2 & 3 take much longer
                self.change_state("chase", cooldown=cd)
            else:
                self.change_state("patrol")

    # ------------------------------------------------------------------
    # Despacho de habilidades por fase
    # ------------------------------------------------------------------

    def _spawn_cultist_attack(self) -> None:
        e = self.entity
        if e.player is None:
            return

        direction = 1.0 if e.facing == "right" else -1.0
        base_y = float(e.hitbox.bottom)
        sx = float(e.hitbox.right if direction > 0 else e.hitbox.left)
        target_x = float(e.player.hitbox.centerx)
        target_y = float(e.player.hitbox.centery)

        phase = getattr(e, "boss_phase", 1)
        if phase == 1:
            # Fase 1: Onda Rasante terrestre (esquivable saltando a plataformas)
            e.spawn_ground_shockwave(sx, base_y + 16.0, direction, speed=165.0, damage=14)
        elif phase == 2:
            # Fase 2: Orbe del Vacío flotante lento dirigido al jugador
            e.spawn_void_orb(sx, base_y - 24.0, target_x, target_y, speed=85.0, damage=16)
        else:
            # Fase 3: Combo total — ambos ataques simultáneos
            e.spawn_ground_shockwave(sx, base_y + 16.0, direction, speed=170.0, damage=15)
            e.spawn_void_orb(sx, base_y - 24.0, target_x, target_y, speed=90.0, damage=16)
