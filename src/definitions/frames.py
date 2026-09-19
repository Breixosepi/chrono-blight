"""
Chrono Blight - Enemy & Special Frames Generator
"""
import pathlib
from typing import Any, Callable, Dict, List, Optional, Tuple
import pygame
from gale import frames


def load_image_sequence(
    folder: pathlib.Path,
    prefix: str,
    count: int,
    pad_fn: Optional[Callable[[pygame.Surface], pygame.Surface]] = None,
) -> List[pygame.Surface]:
    surfaces = [
        pygame.image.load(folder / f"{prefix}_{i}.png")
        for i in range(1, count + 1)
    ]
    return [pad_fn(s) for s in surfaces] if pad_fn else surfaces


def pad_skeleton_frame(surf_50x48: pygame.Surface) -> pygame.Surface:
    canvas = pygame.Surface((100, 65), pygame.SRCALPHA)
    canvas.blit(surf_50x48, (15, 17))
    return canvas

def load_big_monster_frames(
    base_dir: pathlib.Path,
) -> Tuple[List[pygame.Surface], Dict[str, List[pygame.Surface]]]:
    bm_dir = base_dir / "assets" / "graphics" / "entity" / "bosses" / "big_monster"
    
    body_sheets = [
        "dark fantasy big boss idle.png",
        "dark fantasy big boss walk.png",
        "dark fantasy big boss attack 2.png",
        "dark fantasy big boss hit.png",
        "dark fantasy big boss death.png",
    ]
    
    body_frames: List[pygame.Surface] = []
    for file_name in body_sheets:
        tex = pygame.image.load(bm_dir / file_name)
        for rect in frames.generate_frames(tex, 80, 64):
            body_frames.append(tex.subsurface(rect))

    vines_files = {
        "2a":   "dark fantasy big boss attack 2a.png",
        "2b":   "dark fantasy big boss attack 2b.png",
        "2c":   "dark fantasy big boss attack 2c.png",
        "miss": "dark fantasy big boss attack 2 miss.png",
    }
    
    vines_frames: Dict[str, List[pygame.Surface]] = {}
    for key, file_name in vines_files.items():
        tex = pygame.image.load(bm_dir / file_name)
        vines_frames[key] = [
            tex.subsurface(rect) for rect in frames.generate_frames(tex, 48, 48)
        ]

    return body_frames, vines_frames


def load_cultist_frames(base_dir: pathlib.Path) -> List[pygame.Surface]:
    cp_dir = base_dir / "assets" / "graphics" / "entity" / "bosses" / "cultist_priest"
    animations = [
        ("cultist_priest_idle", 5),
        ("cultist_priest_walk", 6),
        ("cultist_priest_attack", 5),
        ("cultist_priest_takehit", 4),
        ("cultist_priest_die", 6),
    ]
    cultist_frames: List[pygame.Surface] = []
    for prefix, count in animations:
        cultist_frames.extend(load_image_sequence(cp_dir, prefix, count))
    return cultist_frames


def load_effect_row(
    image_path: pathlib.Path,
    frame_w: int = 64,
    frame_h: int = 64,
    row_idx: int = 1,
) -> List[pygame.Surface]:
    sheet = pygame.image.load(image_path)
    all_rects = frames.generate_frames(sheet, frame_w, frame_h)
    cols = sheet.get_width() // frame_w
    
    start = row_idx * cols
    end = start + cols
    return [sheet.subsurface(r).copy() for r in all_rects[start:end]]


def load_crown_frames(base_dir: pathlib.Path) -> List[pygame.Surface]:
    crown_dir = base_dir / "assets" / "graphics" / "entity" / "enemies" / "crown"
    sheets = [
        "crow_idle.png",
        "crow_walk.png",
        "crow_jump.png",
        "crow_attack.png",
        "crow_damage.png",
        "crow_death1.png",
        "crow_death2.png",
    ]
    crown_frames: List[pygame.Surface] = []
    for sheet_name in sheets:
        tex = pygame.image.load(crown_dir / sheet_name)
        for rect in frames.generate_frames(tex, 64, 64):
            crown_frames.append(tex.subsurface(rect))
    return crown_frames


def load_skeleton_frames(base_dir: pathlib.Path) -> List[pygame.Surface]:
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


def load_monster2_boss_frames(textures: Dict[str, pygame.Surface]) -> List[pygame.Surface]:
    tex = textures.get("monster2")
    if not tex:
        return []
    rects = frames.generate_frames(tex, 48, 48)
    return [pygame.transform.scale(tex.subsurface(r), (86, 86)) for r in rects]


def load_harvester_frames(base_dir: pathlib.Path) -> List[pygame.Surface]:
    h_file = base_dir / "assets" / "graphics" / "entity" / "bosses" / "The_harvester" / "TheHarvester.png"
    tex = pygame.image.load(h_file)
    fw, fh = 105, 86
    anim_rows = [
        (0, 14),  
        (1, 7),   
        (2, 13),  
        (3, 13),  
        (4, 5),   
        (5, 20),  
    ]
    harvester_frames: List[pygame.Surface] = []
    for r, count in anim_rows:
        for c in range(count):
            rect = pygame.Rect(c * fw, r * fh, fw, fh)
            sub = tex.subsurface(rect)
            canvas = pygame.Surface((fw, fh), pygame.SRCALPHA)
            canvas.blit(sub, (7, 0))
            
            scaled = pygame.transform.scale(canvas, (int(fw * 1.65), int(fh * 1.65)))
            harvester_frames.append(scaled)
    return harvester_frames


def load_monolith_frames(base_dir: pathlib.Path) -> List[pygame.Surface]:
    tex = pygame.image.load(base_dir / "assets" / "graphics" / "traps" / "monolith" / "animation" / "monolith_animation_sheet.png")
    rects = frames.generate_frames(tex, 54, 169)
    return [tex.subsurface(r) for r in rects[:38]]


def load_wind_blade_variants(
    image_path: pathlib.Path,
    row_idx: int,
) -> Tuple[List[pygame.Surface], List[pygame.Surface]]:
    sheet = pygame.image.load(image_path)
    all_rects = frames.generate_frames(sheet, 64, 64)
    cols = sheet.get_width() // 64
    start = row_idx * cols
    raw = [sheet.subsurface(r) for r in all_rects[start:start + cols]]

    # Horizontal: frames 2 & 3 scaled wide and low (ground crescent)
    h_frames = []
    for idx in (2, 3):
        bb = raw[idx].get_bounding_rect()
        tight = raw[idx].subsurface(bb)
        h_frames.append(pygame.transform.scale(tight, (46, 20)))

    # Vertical: frames 4 & 6 scaled tall and imposing (tall wave)
    v_frames = []
    for idx in (4, 6):
        bb = raw[idx].get_bounding_rect()
        tight = raw[idx].subsurface(bb)
        v_frames.append(pygame.transform.scale(tight, (28, 58)))

    return h_frames, v_frames


def generate_enemy_frames(
    base_dir: pathlib.Path,
    textures: Dict[str, pygame.Surface],
) -> Dict[str, Any]:
    effects_dir = base_dir / "assets" / "graphics" / "effects"
    bm_body, bm_vines = load_big_monster_frames(base_dir)

    wb_green_h, wb_green_v = load_wind_blade_variants(effects_dir / "wind_blade.png", row_idx=3)
    wb_red_h, wb_red_v = load_wind_blade_variants(effects_dir / "wind_blade.png", row_idx=7)

    return {
        "skeleton_sword":           load_skeleton_frames(base_dir),
        "monster_eyes":             frames.generate_frames(textures["monster_eyes"], 48, 48),
        "cultist_priest":           load_cultist_frames(base_dir),
        "the_harvester":            load_harvester_frames(base_dir),
        "goblin":                   frames.generate_frames(textures["goblin"], 64, 64),
        "big_monster":              bm_body,
        "crown":                    load_crown_frames(base_dir),
        "boss_vines":               bm_vines,
        "monster2":                 frames.generate_frames(textures["monster2"], 48, 48),
        "monster2_boss":            load_monster2_boss_frames(textures),
        "monster3":                 frames.generate_frames(textures["monster3"], 64, 64),
        "void_orb_frames":          load_effect_row(effects_dir / "void_orb.png", 64, 64, row_idx=1),
        "ground_shockwave_frames":  load_effect_row(effects_dir / "ground_shockwave.png", 64, 64, row_idx=1),
        "burst_frames":             load_effect_row(effects_dir / "burst.png", 64, 64, row_idx=5),
        "side_shoot_frames":        load_effect_row(effects_dir / "side_shoot.png", 64, 64, row_idx=5),
        "wind_blade_green_frames":  load_effect_row(effects_dir / "wind_blade.png", 64, 64, row_idx=3),
        "wind_blade_red_frames":    load_effect_row(effects_dir / "wind_blade.png", 64, 64, row_idx=7),
        "wind_blade_green_horiz":   wb_green_h,
        "wind_blade_green_vert":    wb_green_v,
        "wind_blade_red_horiz":     wb_red_h,
        "wind_blade_red_vert":      wb_red_v,
        "explosion_slash_green_frames": load_effect_row(effects_dir / "explosion.png", 64, 64, row_idx=3)[:3],
        "explosion_burst_green_frames": load_effect_row(effects_dir / "explosion.png", 64, 64, row_idx=3)[3:12],
        "explosion_slash_red_frames":   load_effect_row(effects_dir / "explosion.png", 64, 64, row_idx=7)[:3],
        "explosion_burst_red_frames":   load_effect_row(effects_dir / "explosion.png", 64, 64, row_idx=7)[3:12],
        "monolith_frames":              load_monolith_frames(base_dir),
    }