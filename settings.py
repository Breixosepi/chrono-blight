import pathlib
import pygame
from gale import frames
from gale import input_handler

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
TILE_COLS = VIRTUAL_WIDTH  // TILE_SIZE
TILE_ROWS = VIRTUAL_HEIGHT // TILE_SIZE

PHASE_PAST   = "past"   
PHASE_FUTURE = "future"  

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
}

FRAMES = {
    "sword_red":      frames.generate_frames(TEXTURES["sword_red"],  128, 64),
    "sword_green":    frames.generate_frames(TEXTURES["sword_green"], 128, 64),
    "morph_red":      frames.generate_frames(TEXTURES["morph_red"],  128, 64),
    "morph_green":    frames.generate_frames(TEXTURES["morph_green"], 128, 64),
    "mage_red":       frames.generate_frames(TEXTURES["mage_red"],  128, 64),
    "mage_green":     frames.generate_frames(TEXTURES["mage_green"], 128, 64),
    "mage_atk2_red":  frames.generate_frames(TEXTURES["mage_atk2_red"],  128, 64),
    "mage_atk2_green":frames.generate_frames(TEXTURES["mage_atk2_green"], 128, 64),
    "flame_purple":   frames.generate_frames(TEXTURES["flame_purple"], 64, 64),
    "flame_green":    frames.generate_frames(TEXTURES["flame_green"],   64, 64),
}

pygame.font.init()
FONTS = {
    "hud":   pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minimal4.ttf", 14),
    "ui":    pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minimal4.ttf", 16),
    "title": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minimal4.ttf", 24),
}


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
