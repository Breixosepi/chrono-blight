import pathlib
import pygame
from gale import frames
from gale import input_handler
from src.definitions.frames import generate_enemy_frames
import gale.text
from typing import Optional

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE,"quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN,"enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT,"move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT,"move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP,"up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE,"jump")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_z,"attack")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_x,"special")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_c,"dash")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LSHIFT,"phase_shift")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_q,"prev_form")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_e,"next_form")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LCTRL,"run")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_p,"pause")

TITLE = "Chrono Blight"

BASE_DIR = pathlib.Path(__file__).parent

VIRTUAL_WIDTH  = 320
VIRTUAL_HEIGHT = 180
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720

TILE_SIZE = 16

TEXTURES = {
    "sword_red":      pygame.image.load(BASE_DIR / "assets" / "graphics" / "Sword.png"),
    "sword_green":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "sword_green.png"),
    "morph_red":      pygame.image.load(BASE_DIR / "assets" / "graphics" / "Morph.png"),
    "morph_green":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "Morph_green.png"),
    "mage_red":       pygame.image.load(BASE_DIR / "assets" / "graphics" / "Mage_.png"),
    "mage_green":     pygame.image.load(BASE_DIR / "assets" / "graphics" / "Mage_green.png"),
    "mage_atk2_red":  pygame.image.load(BASE_DIR / "assets" / "graphics" / "mage_atk2.png"),
    "mage_atk2_green":pygame.image.load(BASE_DIR / "assets" / "graphics" / "mage_atk2_green.png"),
    "flame_purple":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "flame_purple.png"),
    "flame_green":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "flame_green.png"),
    "skeleton_sword": pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "skeleton_sword" / "ready_1.png"),
    "monster_eyes":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "monster_eyes" / "monster001eyes.png"),
    "cultist_priest": pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "cultist_priest" / "cultist_priest_idle_1.png"),
    "goblin":         pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "goblin" / "goblin.png"),
    "big_monster":    pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "big monster" / "dark fantasy big boss idle.png"),
    "crown":          pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "crown" / "crow_idle.png"),
    "monster2":       pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "monster2" / "monster2.png"),
    "monster3":       pygame.image.load(BASE_DIR / "assets" / "graphics" / "monsters" / "monster3" / "monster3.png"),
    "abismo_1_past":   pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "abismo_1_past.png"),
    "abismo_1_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "abismo_1_future.png"),
    "sala_past": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "sala_past.png"),
    "sala_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "sala_future.png"),
    "subida_past": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "subida_past.png"),
    "subida_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "subida_future.png"),
    "middle_past": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "middle_past.png"),
    "middle_future": pygame.image.load(BASE_DIR / "assets" / "graphics" / "backgrounds" / "middle_future.png"),
}

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
    **generate_enemy_frames(BASE_DIR, TEXTURES),
}

BOSS_VINES_FRAMES = FRAMES["boss_vines"]

pygame.font.init()
FONTS = {
    "hud":   pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minimal4.ttf", 14),
    "ui":    pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minimal4.ttf", 16),
    "title": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minimal4.ttf", 24),
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
) -> None:
    text_obj: pygame.Surface = font.render(text, False, color, bgcolor)
    text_rect: pygame.Rect = text_obj.get_rect()

    if center:
        text_rect.center = (int(x), int(y))
    else:
        text_rect.x = int(x)
        text_rect.y = int(y)

    if shadowed:
        shadow_text: pygame.Surface = font.render(text, False, (0, 0, 0))
        shadow_rect: pygame.Rect = shadow_text.get_rect()
        shadow_rect.x = text_rect.x + 1
        shadow_rect.y = text_rect.y + 1
        surface.blit(shadow_text, shadow_rect)

    surface.blit(text_obj, text_rect)

gale.text.render_text = _crisp_render_text

SOUNDS: dict = {}
"""
Claves previstas:
  "ambient_past"   -- musica de fondo del Pasado
  "ambient_future" -- musica de fondo del Futuro
  "phase_shift"    -- SFX del cambio de fase
  "attack"         -- SFX del ataque de las 3 formas
  "jump"           -- SFX del salto
  "hurt"           -- SFX de dano recibido
"""
