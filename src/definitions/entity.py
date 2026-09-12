"""
Chrono Blight - Entity Definitions
"""

PLAYER_HIT_W = 16
PLAYER_HIT_H = 24

GRAVITY = 700.0
JUMP_VELOCITY = -280.0
WALK_SPEED = 80.0
RUN_SPEED = 150.0

FLAME_FRAMES = 30
MAGE_AREA_CIRCLES = [
    [6, 7, 8, 9, 10, 11],
    [0, 1, 2, 3, 4, 5],
    [12, 13, 14, 15, 16, 17],
]

_SWORD_ANIMATIONS = {
    "idle":           {"frames": [0, 1, 2, 3, 4, 5, 6], "interval": 1/5.0,  "loops": None},
    "walk":           {"frames": [28, 29, 30, 31, 32, 33, 34, 35], "interval": 1/8.0, "loops": None},
    "run":            {"frames": [42, 43, 44, 45, 46, 47, 48], "interval": 1/10.0, "loops": None},
    "jump":           {"frames": [14, 15, 16, 17], "interval": 1/6.0,  "loops": None},
    "attack":         {"frames": [56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69], "interval": 1/14.0, "loops": 1},
    "attack_up":      {"frames": [63, 64, 65, 66, 67, 68, 69], "interval": 1/14.0, "loops": 1},
    "attack_special": {"frames": [70, 71, 72, 73, 74, 75, 76], "interval": 1/9.0, "loops": 1},
    "hit":            {"frames": [84, 85], "interval": 1/6.0,  "loops": 1},
    "death":          {"frames": [98, 99, 100, 101, 102, 103, 104, 105, 106], "interval": 1/7.0, "loops": 1},
}

_MORPH_ANIMATIONS = {
    "idle":           {"frames": [0, 1, 2, 3, 4, 5], "interval": 1/5.0,  "loops": None},
    "walk":           {"frames": [8, 9, 10, 11, 12, 13], "interval": 1/8.0, "loops": None},
    "jump":           {"frames": [0, 1], "interval": 1/6.0,  "loops": None},
    "dash":           {"frames": [24, 25, 26, 27, 28], "interval": 1/10.0, "loops": 1},
    "attack":         {"frames": [32, 33, 34, 35, 36, 37, 38, 39], "interval": 1/12.0, "loops": 1},
    "attack_special": {"frames": [40, 41, 42, 43, 44, 45], "interval": 1/8.0, "loops": 1},
    "hit":            {"frames": [16, 17], "interval": 1/6.0,  "loops": 1},
    "death":          {"frames": [48, 49, 50, 51, 52, 53, 54, 55], "interval": 1/7.0, "loops": 1},
}

_MAGE_ANIMATIONS = {
    "idle":           {"frames": [0, 1, 2, 3, 4, 5, 6], "interval": 1/5.0,  "loops": None},
    "walk":           {"frames": [10, 11, 12, 13, 14, 15], "interval": 1/8.0, "loops": None},
    "jump":           {"frames": [0, 1], "interval": 1/6.0,  "loops": None},
    "dash":           {"frames": [30, 31, 32, 33, 34], "interval": 1/10.0, "loops": 1},
    "attack":         {"frames": [20, 21, 22, 23, 24, 25, 26, 27, 28], "interval": 1/12.0, "loops": 1},
    "attack_special": {"frames": [30, 31, 32, 33, 34, 35, 36, 37, 38, 39], "interval": 1.2/10.0, "loops": 1},
    "hit":            {"frames": [40], "interval": 1/6.0,  "loops": 1},
    "death":          {"frames": [50, 51, 52, 53, 54, 55, 56, 57], "interval": 1/7.0, "loops": 1},
}

def _character_attack(entity, target=None):
    action = entity.get_action("attack")
    damage = action.get("damage", 10)
    if target is not None and hasattr(target, "damage"):
        target.damage(damage)
    return damage

_player_basic_attack = _character_attack


def _character_attack_aoe(entity, targets=None):
    action = entity.get_action("special")
    damage = action.get("damage", 50)
    hit_count = 0
    if targets:
        for target in targets:
            if hasattr(target, "damage"):
                target.damage(damage)
                hit_count += 1
    return damage, hit_count

#damage and dash
def _sword_special_finish(entity):
    dash_distance = 78.0
    if entity.facing == "right":
        entity.x += dash_distance
    else:
        entity.x -= dash_distance
    entity.hitbox.x = int(entity.x)


def _mage_special_update(entity, dt):
    entity.area_active = True
    circle_fps = 12.0
    total_area_frame = int(entity._anim_timer * circle_fps)
    new_circle_idx = min(2, total_area_frame // 6)
    entity.area_subframe = total_area_frame % 6

    if new_circle_idx != entity.area_circle_idx or (
        new_circle_idx == 0 and total_area_frame == 0 and entity._anim_timer <= dt
    ):
        offsets_x = [45, 105, 175]
        base_offset = offsets_x[new_circle_idx]
        circle_offset_x = base_offset if entity.facing == "right" else -base_offset
        spawn_x = entity.hitbox.centerx + circle_offset_x
        spawn_y = entity.hitbox.bottom

        entity.flames.append({
            "x":     spawn_x,
            "y":     spawn_y,
            "idx":   new_circle_idx,
            "timer": 0.0,
        })

    entity.area_circle_idx = new_circle_idx


def _mage_special_finish(entity):
    entity.area_active = False


def _morph_special_finish(entity):
    pass


def _morph_dash(entity):
    entity.dash_speed = 220.0


def _entity_take_damage(entity, amount: float, source=None) -> float:
    if hasattr(entity, "health"):
        entity.health = max(0.0, entity.health - amount)
        if entity.health <= 0.0 and hasattr(entity, "change_state") and getattr(entity, "state_name", "") != "death":
            entity.change_state("death")
    return amount


def _entity_heal(entity, amount: float) -> float:
    if hasattr(entity, "health") and hasattr(entity, "MAX_HEALTH"):
        entity.health = min(entity.MAX_HEALTH, entity.health + amount)
    return amount


def _enemy_melee_attack(entity, target=None):
    action = entity.get_action("attack") if hasattr(entity, "get_action") else {}
    damage = action.get("damage", 10)
    if target is not None and hasattr(target, "damage"):
        target.damage(damage)
    return damage


_ENTITY_ANIMATIONS = {
    "player": {
        "sword": _SWORD_ANIMATIONS,
        "morph": _MORPH_ANIMATIONS,
        "mage":  _MAGE_ANIMATIONS,
    },
    "enemies": {}
}

ENTITY_DEFS = {
    "animations": _ENTITY_ANIMATIONS,

    "player": {
        "hitbox": {"width": PLAYER_HIT_W, "height": PLAYER_HIT_H},
        
        "physics": {
            "gravity": GRAVITY,
            "jump_velocity": JUMP_VELOCITY,
            "walk_speed": WALK_SPEED,
            "run_speed": RUN_SPEED,
        },

        "mage_area": {
            "circles": MAGE_AREA_CIRCLES,
            "flame_frames": FLAME_FRAMES,
        },

        "forms": {
            "sword": {
                "name": "Swordmaster",
                "stats": {
                    "max_health": 80,
                    "max_mana":   50,
                    "mana_regen": 3.0,
                    "jumps":      2,
                },
                "actions": {
                    "attack": {
                        "name": "Sword Slash Combo",
                        "func": _player_basic_attack,
                        "damage": 15,
                        "mana_cost": 0,
                        "combo": {
                            "hit1_frames": 7,
                            "hit2_damage": 20,
                        },
                        "up_anim": "attack_up",
                    },
                    "special": {
                        "name": "Thrust Dash",
                        "func": None,
                        "damage": 30,
                        "mana_cost": 20,
                        "on_finish": _sword_special_finish,
                    },
                },
                "combat": {
                    "attack_damage":         15,
                    "attack_mana_cost":       0,
                    "special_damage":        30,
                    "special_mana_cost":     20,
                },
                "offsets": {"right": -18, "left": -94, "y": -27},
            },

            "morph": {
                "name": "Beast Morph",
                "stats": {
                    "max_health": 120,
                    "max_mana":    30,
                    "mana_regen":  2.0,
                    "jumps":       1,
                },
                "actions": {
                    "attack": {
                        "name": "Beast Claw",
                        "func": _player_basic_attack,
                        "damage": 12,
                        "mana_cost": 0,
                    },
                    "special": {
                        "name": "Primal Impact",
                        "func": None,
                        "damage": 20,
                        "mana_cost": 15,
                        "on_finish": _morph_special_finish,
                    },
                    "dash": {
                        "name": "Beast Dash",
                        "func": _morph_dash,
                        "mana_cost": 10,
                        "dash_speed": 220.0,
                    },
                },
                "combat": {
                    "attack_damage":         12,
                    "attack_mana_cost":       0,
                    "special_damage":        20,
                    "special_mana_cost":     15,
                    "dash_cost":             10,
                },
                "offsets": {"right": -23, "left": -89, "y": -26},
            },

            "mage": {
                "name": "Phase Mage",
                "stats": {
                    "max_health": 50,
                    "max_mana":  100,
                    "mana_regen": 10.0,
                    "jumps":       1,
                },
                "actions": {
                    "attack": {
                        "name": "Arcane Bolt",
                        "func": _player_basic_attack,
                        "damage": 18,
                        "mana_cost": 5,
                    },
                    "special": {
                        "name": "Infernal Flame Area",
                        "func": _character_attack_aoe,
                        "is_aoe": True,
                        "damage": 50,
                        "mana_cost": 35,
                        "duration": 1.2,
                        "on_update": _mage_special_update,
                        "on_finish": _mage_special_finish,
                    },
                },
                "combat": {
                    "attack_damage":         18,
                    "attack_mana_cost":       5,
                    "special_damage":        50,
                    "special_mana_cost":     35,
                },
                "offsets": {"right": -29, "left": -83, "y": -23},
            },
        },
    },
}


