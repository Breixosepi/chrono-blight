import pathlib
import pygame
from gale import frames
from gale import input_handler
from src.definitions.frames import generate_enemy_frames
import gale.text
from typing import Optional

from src import controls_manager
controls_manager.load_controls()
controls_manager.apply_controls()

TITLE = "Chrono Blight"

BASE_DIR = pathlib.Path(__file__).parent

VIRTUAL_WIDTH  = 320
VIRTUAL_HEIGHT = 180
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720

TILE_SIZE = 16

TEXTURES = {
    "sword_red":      pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "sword" / "Sword.png"),
    "sword_green":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "sword" / "sword_green.png"),
    "morph_red":      pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "morph" / "Morph.png"),
    "morph_green":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "morph" / "Morph_green.png"),
    "mage_red":       pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "mage" / "Mage_.png"),
    "mage_green":     pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "mage" / "Mage_green.png"),
    "mage_atk2_red":  pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "mage" / "mage_atk2.png"),
    "mage_atk2_green":pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "mage" / "mage_atk2_green.png"),
    "flame_purple":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "mage" / "flame_purple.png"),
    "flame_green":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "player" / "mage" / "flame_green.png"),
    "skeleton_sword": pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "enemies" / "skeleton_sword" / "ready_1.png"),
    "monster_eyes":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "enemies" / "monster_eyes" / "monster001eyes.png"),
    "goblin":         pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "enemies" / "goblin" / "goblin.png"),
    "crown":          pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "enemies" / "crown" / "crow_idle.png"),
    "monster2":       pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "enemies" / "monster2" / "monster2.png"),
    "monster3":       pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "enemies" / "monster3" / "monster3.png"),
    "cultist_priest": pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "bosses" / "cultist_priest" / "cultist_priest_idle_1.png"),
    "big_monster":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "bosses" / "big_monster" / "dark fantasy big boss idle.png"),
    "the_harvester":  pygame.image.load(BASE_DIR / "assets" / "graphics" / "entity" / "bosses" / "The_harvester" / "TheHarvester.png"),
    "abismo_1_past":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "abismo_1_past.png"),
    "abismo_1_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "abismo_1_future.png"),
    "sala_past":       pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "sala_past.png"),
    "sala_future":     pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "sala_future.png"),
    "subida_past":     pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "subida_past.png"),
    "subida_future":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "subida_future.png"),
    "middle_past":     pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "middle_past.png"),
    "middle_future":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "middle_future.png"),
    "big_room_past":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "b_r_past.png"),
    "big_room_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "b_r_future.png"),
    "void_orb":          pygame.image.load(BASE_DIR / "assets" / "graphics" / "effects" / "void_orb.png"),
    "wind_blade":        pygame.image.load(BASE_DIR / "assets" / "graphics" / "effects" / "wind_blade.png"),
    "explosion":         pygame.image.load(BASE_DIR / "assets" / "graphics" / "effects" / "explosion.png"),
    "monolith":          pygame.image.load(BASE_DIR / "assets" / "graphics" / "traps" / "monolith" / "animation" / "monolith_animation_sheet.png"),
    "ground_shockwave":  pygame.image.load(BASE_DIR / "assets" / "graphics" / "effects" / "ground_shockwave.png"),
    "saw_blade":          pygame.image.load(BASE_DIR / "assets" / "graphics" / "traps" / "saws" / "saw_blade.png"),
    "destructible_block": pygame.image.load(BASE_DIR / "assets" / "graphics" / "traps" / "blocks" / "Brick1.png"),
    "moving_platform":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "traps" / "platforms" / "Moving Platfrom_A.png"),
    "elevator_open":      pygame.image.load(BASE_DIR / "assets" / "graphics" / "traps" / "elevator" / "13.png"),
    "elevator_closed":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "traps" / "elevator" / "12.png"),
    "elevator_rope":      pygame.image.load(BASE_DIR / "assets" / "graphics" / "traps" / "elevator" / "22.png"),
    "obelisk":            pygame.image.load(BASE_DIR / "assets" / "graphics" / "world" / "objects" / "obelisk.png"),
    "animated_items":     pygame.image.load(BASE_DIR / "assets" / "graphics" / "items" / "animated_items.png"),
    "keyboard_ui":        pygame.image.load(BASE_DIR / "assets" / "graphics" / "ui" / "keyboard.png"),
    "save_icon":          pygame.image.load(BASE_DIR / "assets" / "graphics" / "ui" / "save_icon.png"),
    "humble_ui":          pygame.image.load(BASE_DIR / "assets" / "graphics" / "ui" / "Humble Gift - v1.3" / "PNG" / "SpriteSheet.png"),
    "gothic_castle_past":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "bg_chrono_blight_past.png"),
    "gothic_castle_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "bg_chrono_blight_future.png"),
    "logo_past":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "logo_past.png"),
    "logo_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "logo_future.png"),
}

SAVE_SLOTS = ["slot_1", "slot_2", "slot_3"]

FRAMES = {
    "sword_red":       frames.generate_frames(TEXTURES["sword_red"],  128, 64),
    "sword_green":     frames.generate_frames(TEXTURES["sword_green"], 128, 64),
    "morph_red":       frames.generate_frames(TEXTURES["morph_red"],  128, 64),
    "morph_green":     frames.generate_frames(TEXTURES["morph_green"], 128, 64),
    "mage_red":        frames.generate_frames(TEXTURES["mage_red"],  128, 64),
    "mage_green":      frames.generate_frames(TEXTURES["mage_green"], 128, 64),
    "mage_atk2_red":   frames.generate_frames(TEXTURES["mage_atk2_red"],  128, 64),
    "mage_atk2_green": frames.generate_frames(TEXTURES["mage_atk2_green"], 128, 64),
    "flame_purple":    frames.generate_frames(TEXTURES["flame_purple"], 64, 64),
    "flame_green":     frames.generate_frames(TEXTURES["flame_green"],   64, 64),
    "saw_blade":          frames.generate_frames(TEXTURES["saw_blade"], 32, 32),
    "destructible_block": frames.generate_frames(TEXTURES["destructible_block"], 32, 32),
    "moving_platform":    frames.generate_frames(TEXTURES["moving_platform"], 32, 16),
    "obelisk":            frames.generate_frames(TEXTURES["obelisk"], 190, 380),
    "save_icon":          frames.generate_frames(TEXTURES["save_icon"], 16, 16),
    "animated_items":     frames.generate_frames(TEXTURES["animated_items"], 32, 32),
    "keyboard_ui":        frames.generate_frames(TEXTURES["keyboard_ui"], 16, 16),
    **generate_enemy_frames(BASE_DIR, TEXTURES),
}

BOSS_VINES_FRAMES = FRAMES["boss_vines"]

pygame.font.init()
FONTS = {
    "hud": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "golden-apple.ttf", 10),
    "hud_small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "golden-apple.ttf", 9),
    "ui": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "golden-apple.ttf", 10),
    "title": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "golden-apple.ttf", 18),
    "title_1": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Undaunted-DEMO.otf", 20),
    "main-title": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Undaunted-DEMO.otf", 24),
}

def _crisp_render_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    x: float,
    y: float,
    color: pygame.Color,
    bgcolor: Optional[pygame.Color] = None,
    center: bool = False,
    shadowed: bool = False,
    clamp_to_surface: bool = True,
) -> None:
    if "\n" in text:
        lines = text.split("\n")
        line_h = font.get_linesize()
        if center:
            total_h = len(lines) * line_h
            start_y = y - total_h / 2.0 + line_h / 2.0
            for i, line in enumerate(lines):
                _crisp_render_text(
                    surface,
                    line,
                    font,
                    x,
                    start_y + i * line_h,
                    color,
                    bgcolor=bgcolor,
                    center=True,
                    shadowed=shadowed,
                    clamp_to_surface=clamp_to_surface,
                )
        else:
            for i, line in enumerate(lines):
                _crisp_render_text(
                    surface,
                    line,
                    font,
                    x,
                    y + i * line_h,
                    color,
                    bgcolor=bgcolor,
                    center=False,
                    shadowed=shadowed,
                    clamp_to_surface=clamp_to_surface,
                )
        return

    text_obj: pygame.Surface = font.render(text, False, color, bgcolor)
    text_rect: pygame.Rect = text_obj.get_rect()

    if center:
        text_rect.center = (int(x), int(y))
    else:
        text_rect.x = int(x)
        text_rect.y = int(y)

    if clamp_to_surface:
        surf_w, surf_h = surface.get_size()
        if text_rect.width <= surf_w - 6:
            if text_rect.left < 2:
                text_rect.left = 2
            elif text_rect.right > surf_w - 3:
                text_rect.right = surf_w - 3
        if text_rect.height <= surf_h - 6:
            if text_rect.top < 2:
                text_rect.top = 2
            elif text_rect.bottom > surf_h - 3:
                text_rect.bottom = surf_h - 3

    if shadowed:
        shadow_text: pygame.Surface = font.render(text, False, (0, 0, 0))
        shadow_rect: pygame.Rect = shadow_text.get_rect()
        shadow_rect.x = text_rect.x + 1
        shadow_rect.y = text_rect.y + 1
        surface.blit(shadow_text, shadow_rect)

    surface.blit(text_obj, text_rect)

gale.text.render_text = _crisp_render_text

SOUNDS = {
    "intro": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "intro.wav"),
    "ambient": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "ambient.mp3"),
    "game-over": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "game_over.mp3"),

    "jump": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "jump.wav"),
    "lava": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "lava.wav"),

    "close": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "close.wav"),
    "open": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "open.wav"),

    "save": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "save.wav"),

    "change": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "change.wav"),
    "enter": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "enter.wav"),
    
    "heart": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "heart.wav"),
    "hit-player": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "hit_player.wav"),
    "enemy-death": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "enemy_death.wav"),

    "boss-wind-spell": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "boss_wind_spell.wav"),

    "morph-power": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "morph_rocks.wav"),
    "morph-fire": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "morph_fire.wav"),
    "morph-dash": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "dash_morph.mp3"),

    "sword": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sword.wav"),
    "sword-dash": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sword_dash.wav"),

    "mage-special": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "mage_special.wav"),
    "mage-attack": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "mage.wav"),

    "giant_boss": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "giant_boss.wav"),
    "boss_survive": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "small_boss.wav"),
    "final_boss": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "final_boss.wav"),

    "phase_shift_past": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "past.wav"),
    "phase_shift_future": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "future.wav"),
    "change-skin": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "change_skin.wav"),
    "on-land": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "on_land.mp3"),

    "rock-crack": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "crumble-rocks.wav"),
    "rock-smash": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "smash.wav"),
    "saw-hazard": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "saw.wav"),
    "lava-shower": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "lava_boss.wav"),
    "arena-cleared": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "arena_fanfare.mp3"),

    "paper-unfold": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "unfold_map.mp3"),
    "paper-fold": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "fold_map.wav"),

    "player-death": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "player_death.wav"),
    "unlock-state": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "unlock_state.wav"),
    "slash-hit": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "hit_flesh.mp3"),
    "shield-active": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "shield_active.mp3"),
    "enemy-hurt": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "enemy_hurt.mp3"),
    
}

MUSIC_CHANNELS = {
    "intro": None,
    "ambient": None,
    "boss_survive": None,
    "giant_boss": None,
    "final_boss": None,
    "game-over": None,
}

def play_music(name: str) -> None:
    stop_music(name)
    MUSIC_CHANNELS[name] = SOUNDS[name].play(loops=-1)


def stop_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.stop()
        MUSIC_CHANNELS[name] = None


def pause_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.pause()


def resume_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.unpause()

def stop_all_music() -> None:
    for name in list(MUSIC_CHANNELS.keys()):
        stop_music(name)
    
    if "lava" in SOUNDS:
        SOUNDS["lava"].stop()

    if "saw-hazard" in SOUNDS:
        SOUNDS["saw-hazard"].stop()

    if "lava-shower" in SOUNDS:
        SOUNDS["lava-shower"].stop()
