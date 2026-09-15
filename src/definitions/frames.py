"""
Chrono Blight - Enemy & Special Frames Generator
"""

from __future__ import annotations

import pathlib
from typing import Any
import pygame
from gale import frames


def slice_strips(texture: pygame.Surface, frame_width: int, frame_height: int) -> list[pygame.Surface]:
    return [
        texture.subsurface(rect)
        for rect in frames.generate_frames(texture, frame_width, frame_height)
    ]


def load_image_sequence(
    folder: pathlib.Path, prefix: str, count: int, pad_fn=None) -> list[pygame.Surface]:
    surfaces = [pygame.image.load(folder / f"{prefix}_{i}.png") for i in range(1, count + 1)]
    return [pad_fn(s) for s in surfaces] if pad_fn else surfaces


def pad_skeleton_frame(surf_50x48: pygame.Surface) -> pygame.Surface:
    canvas = pygame.Surface((100, 65), pygame.SRCALPHA)
    canvas.blit(surf_50x48, (15, 17))
    return canvas


# ---------------------------------------------------------------------------
# Jefes
# ---------------------------------------------------------------------------

def load_big_monster_frames(base_dir: pathlib.Path) -> tuple[list[pygame.Surface], dict[str, list[pygame.Surface]]]:
    bm_dir = base_dir / "assets" / "graphics" / "entity" / "bosses" / "big_monster"
    idle   = pygame.image.load(bm_dir / "dark fantasy big boss idle.png")
    walk   = pygame.image.load(bm_dir / "dark fantasy big boss walk.png")
    atk    = pygame.image.load(bm_dir / "dark fantasy big boss attack 2.png")
    atk_a  = pygame.image.load(bm_dir / "dark fantasy big boss attack 2a.png")
    atk_b  = pygame.image.load(bm_dir / "dark fantasy big boss attack 2b.png")
    atk_c  = pygame.image.load(bm_dir / "dark fantasy big boss attack 2c.png")
    atk_m  = pygame.image.load(bm_dir / "dark fantasy big boss attack 2 miss.png")
    hit    = pygame.image.load(bm_dir / "dark fantasy big boss hit.png")
    death  = pygame.image.load(bm_dir / "dark fantasy big boss death.png")

    body_frames = (
        slice_strips(idle, 80, 64)    # 0..15: idle
        + slice_strips(walk, 80, 64)   # 16..31: walk
        + slice_strips(atk, 80, 64)    # 32..47: attack
        + slice_strips(hit, 80, 64)    # 48..50: hit
        + slice_strips(death, 80, 64)  # 51..66: death
    )

    vines_frames = {
        "2a":   slice_strips(atk_a, 48, 48),
        "2b":   slice_strips(atk_b, 48, 48),
        "2c":   slice_strips(atk_c, 48, 48),
        "miss": slice_strips(atk_m, 48, 48),
    }

    return body_frames, vines_frames


def load_cultist_frames(base_dir: pathlib.Path) -> list[pygame.Surface]:
    cp_dir = base_dir / "assets" / "graphics" / "entity" / "bosses" / "cultist_priest"
    return (
        load_image_sequence(cp_dir, "cultist_priest_idle", 5)
        + load_image_sequence(cp_dir, "cultist_priest_walk", 6)
        + load_image_sequence(cp_dir, "cultist_priest_attack", 5)
        + load_image_sequence(cp_dir, "cultist_priest_takehit", 4)
        + load_image_sequence(cp_dir, "cultist_priest_die", 6)
    )


# ---------------------------------------------------------------------------
# Efectos de habilidades del jefe cultista
# Spritesheet: grids de 64x64 px. Fila 2 (y_offset=64) = color morado/violeta.
# void_orb:         960 x 576  →  15 cols × 9 filas
# ground_shockwave: 896 x 576  →  14 cols × 9 filas
# ---------------------------------------------------------------------------

def load_void_orb_frames(base_dir: pathlib.Path) -> list[pygame.Surface]:
    """Extrae la fila 2 (morado) del spritesheet void_orb.png (64x64 px/frame)."""
    sheet = pygame.image.load(base_dir / "assets" / "graphics" / "effects" / "void_orb.png")
    frame_w, frame_h = 64, 64
    row_y = frame_h  # fila 2 (índice 1) → y = 64
    n_cols = sheet.get_width() // frame_w  # 15
    return [
        sheet.subsurface(pygame.Rect(col * frame_w, row_y, frame_w, frame_h))
        for col in range(n_cols)
    ]


def load_ground_shockwave_frames(base_dir: pathlib.Path) -> list[pygame.Surface]:
    """Extrae la fila 2 (morado) del spritesheet ground_shockwave.png (64x64 px/frame).
    La animación va de izquierda a derecha; al disparar hacia la izquierda se flipea en render.
    """
    sheet = pygame.image.load(base_dir / "assets" / "graphics" / "effects" / "ground_shockwave.png")
    frame_w, frame_h = 64, 64
    row_y = frame_h  # fila 2 (índice 1) → y = 64
    n_cols = sheet.get_width() // frame_w  # 14
    return [
        sheet.subsurface(pygame.Rect(col * frame_w, row_y, frame_w, frame_h))
        for col in range(n_cols)
    ]


# ---------------------------------------------------------------------------
# Enemigos regulares
# ---------------------------------------------------------------------------

def load_crown_frames(base_dir: pathlib.Path) -> list[pygame.Surface]:
    crown_dir = base_dir / "assets" / "graphics" / "entity" / "enemies" / "crown"
    idle   = pygame.image.load(crown_dir / "crow_idle.png")
    walk   = pygame.image.load(crown_dir / "crow_walk.png")
    jump   = pygame.image.load(crown_dir / "crow_jump.png")
    atk    = pygame.image.load(crown_dir / "crow_attack.png")
    damage = pygame.image.load(crown_dir / "crow_damage.png")
    death1 = pygame.image.load(crown_dir / "crow_death1.png")
    death2 = pygame.image.load(crown_dir / "crow_death2.png")

    return (
        slice_strips(idle, 64, 64)    # 0..3: idle
        + slice_strips(walk, 64, 64)   # 4..7: walk
        + slice_strips(jump, 64, 64)   # 8..13: jump
        + slice_strips(atk, 64, 64)    # 14..18: attack
        + slice_strips(damage, 64, 64) # 19..21: hit
        + slice_strips(death1, 64, 64) # 22..26: death
        + slice_strips(death2, 64, 64) # 27..32: death2
    )


def load_skeleton_frames(base_dir: pathlib.Path) -> list[pygame.Surface]:
    sk_dir = base_dir / "assets" / "graphics" / "entity" / "enemies" / "skeleton_sword"
    return (
        load_image_sequence(sk_dir, "ready", 3, pad_skeleton_frame)
        + load_image_sequence(sk_dir, "walk", 6, pad_skeleton_frame)
        + load_image_sequence(sk_dir, "run", 6, pad_skeleton_frame)
        + load_image_sequence(sk_dir, "attack1", 6)
        + load_image_sequence(sk_dir, "attack2", 6)
        + load_image_sequence(sk_dir, "hit", 3, pad_skeleton_frame)
        + load_image_sequence(sk_dir, "dead_near", 6, pad_skeleton_frame)
        + load_image_sequence(sk_dir, "dead_far", 6, pad_skeleton_frame)
        + load_image_sequence(sk_dir, "reborn", 3, pad_skeleton_frame)
    )


def generate_enemy_frames(
    base_dir: pathlib.Path, textures: dict[str, pygame.Surface]
) -> dict[str, Any]:
    bm_body, bm_vines = load_big_monster_frames(base_dir)

    return {
        "skeleton_sword":    load_skeleton_frames(base_dir),
        "monster_eyes":      frames.generate_frames(textures["monster_eyes"], 48, 48),
        "cultist_priest":    load_cultist_frames(base_dir),
        "goblin":            frames.generate_frames(textures["goblin"], 64, 64),
        "big_monster":       bm_body,
        "crown":             load_crown_frames(base_dir),
        "boss_vines":        bm_vines,
        "monster2":          frames.generate_frames(textures["monster2"], 48, 48),
        "monster3":          frames.generate_frames(textures["monster3"], 64, 64),
        # Efectos de habilidades del jefe cultista (fila 2 = morado)
        "void_orb_frames":          load_void_orb_frames(base_dir),
        "ground_shockwave_frames":  load_ground_shockwave_frames(base_dir),
    }
