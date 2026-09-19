import json
import pathlib
import pygame
from gale import input_handler

CONFIG_FILE = pathlib.Path(__file__).parent / "controls.json"

DEFAULT_KEYBINDS = {
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "up": pygame.K_w,
    "down": pygame.K_s,
    "jump": pygame.K_SPACE,
    "attack": pygame.K_j,
    "special": pygame.K_k,
    "dash": pygame.K_LSHIFT,
    "phase_shift": pygame.K_l,
    "prev_form": pygame.K_q,
    "next_form": pygame.K_e,
    "map": pygame.K_m,
    "pause": pygame.K_p,
}

SYSTEM_KEYBINDS = {
    "escape": pygame.K_ESCAPE,
    "back": pygame.K_BACKSPACE,
    "enter": pygame.K_RETURN,
}

ACTION_LABELS = {
    "move_left": "Mover Izquierda",
    "move_right": "Mover Derecha",
    "up": "Arriba / Interactuar",
    "down": "Abajo",
    "jump": "Saltar",
    "attack": "Ataque",
    "special": "Especial",
    "dash": "Dash",
    "phase_shift": "Cambio de Fase",
    "prev_form": "Forma Anterior",
    "next_form": "Forma Siguiente",
    "map": "Mapa",
    "pause": "Pausa",
}

KEY_NAMES = {
    pygame.K_SPACE: "ESPACIO",
    pygame.K_LSHIFT: "L-SHIFT",
    pygame.K_RSHIFT: "R-SHIFT",
    pygame.K_LCTRL: "L-CTRL",
    pygame.K_RCTRL: "R-CTRL",
    pygame.K_LALT: "L-ALT",
    pygame.K_RALT: "R-ALT",
    pygame.K_RETURN: "ENTER",
    pygame.K_BACKSPACE: "RETROCESO",
    pygame.K_TAB: "TAB",
    pygame.K_ESCAPE: "ESC",
    pygame.K_UP: "ARRIBA",
    pygame.K_DOWN: "ABAJO",
    pygame.K_LEFT: "IZQUIERDA",
    pygame.K_RIGHT: "DERECHA",
}

CURRENT_KEYBINDS = dict(DEFAULT_KEYBINDS)

def get_key_name(key_code: int) -> str:
    if key_code in KEY_NAMES:
        return KEY_NAMES[key_code]
    name = pygame.key.name(key_code)
    return name.upper() if name else f"KEY_{key_code}"

def load_controls() -> dict:
    global CURRENT_KEYBINDS
    CURRENT_KEYBINDS = dict(DEFAULT_KEYBINDS)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for action, key in data.items():
                if action in CURRENT_KEYBINDS:
                    CURRENT_KEYBINDS[action] = int(key)
        except Exception:
            pass
    return CURRENT_KEYBINDS

def save_controls(controls_dict: dict = None) -> None:
    global CURRENT_KEYBINDS
    if controls_dict is not None:
        CURRENT_KEYBINDS = dict(controls_dict)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(CURRENT_KEYBINDS, f, indent=4)
    except Exception:
        pass

def apply_controls() -> None:
    input_handler.InputHandler.input_binding["keyboard"].clear()
    for action, key in SYSTEM_KEYBINDS.items():
        input_handler.InputHandler.set_keyboard_action(key, action)
    for action, key in CURRENT_KEYBINDS.items():
        input_handler.InputHandler.set_keyboard_action(key, action)

def set_control(action: str, key_code: int) -> None:
    CURRENT_KEYBINDS[action] = key_code
    save_controls()
    apply_controls()

def reset_to_defaults() -> None:
    global CURRENT_KEYBINDS
    CURRENT_KEYBINDS = dict(DEFAULT_KEYBINDS)
    save_controls()
    apply_controls()

def is_up_key_pressed(keys=None) -> bool:
    if keys is None:
        keys = pygame.key.get_pressed()
    up_key = CURRENT_KEYBINDS.get("up", pygame.K_w)
    return bool(keys[up_key] or keys[pygame.K_UP])

