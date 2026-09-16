"""
Chrono Blight - Entity Definitions
"""

from typing import Any, Dict

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

# Player animations

_SWORD_ANIMATIONS = {
    "idle":           {"frames": [0, 1, 2, 3, 4, 5, 6], "interval": 1/5.0,  "loops": None},
    "walk":           {"frames": [28, 29, 30, 31, 32, 33, 34, 35], "interval": 1/8.0, "loops": None},
    "run":            {"frames": [42, 43, 44, 45, 46, 47, 48], "interval": 1/10.0, "loops": None},
    "jump":           {"frames": [15], "interval": 1.0,  "loops": 1},
    "fall":           {"frames": [16], "interval": 1.0,  "loops": 1},
    "attack":         {"frames": [56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69], "interval": 1/15.0, "loops": 1},
    "attack_up":      {"frames": [63, 64, 65, 66, 67, 68, 69], "interval": 1/11.0, "loops": 1},
    "attack_special": {"frames": [70, 71, 72, 73, 74, 75, 76], "interval": 1/9.0, "loops": 1},
    "hit":            {"frames": [84, 85], "interval": 1/6.0,  "loops": 1},
    "death":          {"frames": [98, 99, 100, 101, 102, 103, 104, 105, 106], "interval": 1/7.0, "loops": 1},
}

_MORPH_ANIMATIONS = {
    "idle":           {"frames": [0, 1, 2, 3, 4, 5], "interval": 1/5.0,  "loops": None},
    "walk":           {"frames": [8, 9, 10, 11, 12, 13], "interval": 1/8.0, "loops": None},
    "jump":           {"frames": [0, 1], "interval": 1/6.0,  "loops": None},
    "fall":           {"frames": [0, 1], "interval": 1/6.0,  "loops": None},
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
    "fall":           {"frames": [0, 1], "interval": 1/6.0,  "loops": None},
    "dash":           {"frames": [30, 31, 32, 33, 34], "interval": 1/10.0, "loops": 1},
    "attack":         {"frames": [20, 21, 22, 23, 24, 25, 26, 27, 28], "interval": 1/12.0, "loops": 1},
    "attack_special": {"frames": [30, 31, 32, 33, 34, 35, 36, 37, 38, 39], "interval": 1.2/10.0, "loops": 1},
    "hit":            {"frames": [40], "interval": 1/6.0,  "loops": 1},
    "death":          {"frames": [50, 51, 52, 53, 54, 55, 56, 57], "interval": 1/7.0, "loops": 1},
}

# Enemy Animations

_SKELETON_SWORD_ANIMATIONS = {
    "idle":    {"frames": [0, 1, 2],                 "interval": 1/5.0, "loops": None},
    "walk":    {"frames": list(range(3, 9)),         "interval": 1/8.0, "loops": None},
    "run":     {"frames": list(range(9, 15)),        "interval": 1/9.0, "loops": None},
    "attack":  {"frames": list(range(15, 21)),       "interval": 1/10.0, "loops": 1},
    "attack2": {"frames": list(range(21, 27)),       "interval": 1/10.0, "loops": 1},
    "hit":     {"frames": [27, 28, 29],              "interval": 1/8.0, "loops": 1},
    "death":   {"frames": list(range(30, 36)),       "interval": 1/8.0, "loops": 1},
    "death2":  {"frames": list(range(36, 42)),       "interval": 1/8.0, "loops": 1},
    "reborn":  {"frames": [42, 43, 44],              "interval": 1/6.0, "loops": 1},
}

_MONSTER_EYES_ANIMATIONS = {
    "idle":    {"frames": [0, 1, 2, 3, 4, 5, 6, 7], "interval": 1/7.0, "loops": None},
    "walk":    {"frames": [8, 9, 10, 11, 12, 13, 14, 15], "interval": 1/8.0, "loops": None},
    "walk2":   {"frames": [16, 17, 18, 19, 20, 21, 22, 23], "interval": 1/8.0, "loops": None},
    "attack":  {"frames": [24, 25, 26, 27, 28, 29, 30, 31], "interval": 1/10.0, "loops": 1},
    "attack2": {"frames": [32, 33, 34, 35, 36, 37, 38, 39], "interval": 1/10.0, "loops": 1},
    "hit":     {"frames": [40, 41, 42], "interval": 1/8.0, "loops": 1},
    "death":   {"frames": [48, 49, 50, 51, 52, 53, 54, 55], "interval": 1/7.0, "loops": 1},
    "death2":  {"frames": [56, 57, 58, 59, 60, 61, 62, 63], "interval": 1/7.0, "loops": 1},
}

_CULTIST_PRIEST_ANIMATIONS = {
    "idle":   {"frames": list(range(0, 5)),   "interval": 1/6.0, "loops": None},
    "walk":   {"frames": list(range(5, 11)),  "interval": 1/8.0, "loops": None},
    "attack": {"frames": list(range(11, 16)), "interval": 1/8.0, "loops": 1},
    "hit":    {"frames": list(range(16, 20)), "interval": 1/8.0, "loops": 1},
    "death":  {"frames": list(range(20, 26)), "interval": 1/7.0, "loops": 1},
}

_GOBLIN_ANIMATIONS = {
    "idle":    {"frames": [64, 65, 66, 67, 68, 69, 70, 71], "interval": 1/7.0, "loops": None},
    "walk":    {"frames": [80, 81, 82, 83, 84, 85, 86, 87], "interval": 1/8.0, "loops": None},
    "run":     {"frames": [96, 97, 98, 99, 100, 101, 102, 103], "interval": 1/9.0, "loops": None},
    "attack":  {"frames": [128, 129, 130, 131, 132, 133, 134, 135], "interval": 1/10.0, "loops": 1},
    "attack2": {"frames": [144, 145, 146, 147, 148, 149, 150, 151], "interval": 1/10.0, "loops": 1},
    "hit":     {"frames": [240, 241, 242], "interval": 1/8.0, "loops": 1},
    "death":   {"frames": [256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267], "interval": 1/8.0, "loops": 1},
    "death2":  {"frames": list(range(272, 288)), "interval": 1/8.0, "loops": 1},
}

_BIG_MONSTER_ANIMATIONS = {
    "idle":   {"frames": list(range(0, 16)), "interval": 1/8.0, "loops": None},
    "walk":   {"frames": list(range(16, 32)), "interval": 1/8.0, "loops": None},
    "attack": {"frames": list(range(32, 48)), "interval": 1/10.0, "loops": 1},
    "hit":    {"frames": [48, 49, 50], "interval": 1/8.0, "loops": 1},
    "death":  {"frames": list(range(51, 67)), "interval": 1/8.0, "loops": 1},
}

_CROWN_ANIMATIONS = {
    "idle":   {"frames": list(range(0, 4)), "interval": 1/6.0, "loops": None},
    "walk":   {"frames": list(range(4, 8)), "interval": 1/8.0, "loops": None},
    "jump":   {"frames": list(range(8, 14)), "interval": 1/8.0, "loops": None},
    "attack": {"frames": list(range(14, 19)), "interval": 1/9.0, "loops": 1},
    "hit":    {"frames": [19, 20, 21], "interval": 1/8.0, "loops": 1},
    "death":  {"frames": list(range(22, 27)), "interval": 1/7.0, "loops": 1},
    "death2": {"frames": list(range(27, 33)), "interval": 1/7.0, "loops": 1},
}

_MONSTER2_ANIMATIONS = {
    "idle":    {"frames": list(range(0, 8)),   "interval": 1/8.0, "loops": None},
    "walk":    {"frames": list(range(10, 18)), "interval": 1/8.0, "loops": None},
    "attack":  {"frames": list(range(40, 48)), "interval": 1/10.0, "loops": 1},
    "attack2": {"frames": list(range(50, 60)), "interval": 1/10.0, "loops": 1},
    "hit":     {"frames": [20, 21, 22],        "interval": 1/8.0, "loops": 1},
    "death":   {"frames": list(range(20, 30)), "interval": 1/8.0, "loops": 1},
    "death2":  {"frames": list(range(30, 38)), "interval": 1/8.0, "loops": 1},
}

_MONSTER3_ANIMATIONS = {
    "idle":      {"frames": list(range(0, 8)),     "interval": 1/8.0, "loops": None},
    "walk":      {"frames": list(range(18, 26)),   "interval": 1/8.0, "loops": None},
    "attack":    {"frames": list(range(36, 46)),   "interval": 1/10.0, "loops": 1},
    "attack2":   {"frames": list(range(54, 68)),   "interval": 1/11.0, "loops": 1},
    "hit":       {"frames": [72, 73, 74],          "interval": 1/8.0, "loops": 1},
    "death":     {"frames": list(range(90, 104)),  "interval": 1/9.0, "loops": 1},
    "awakening": {"frames": list(range(108, 126)), "interval": 1/10.0, "loops": 1},
}

# Entity Definitions (Data Only)

ENTITY_DEFS: Dict[str, Any] = {
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
                    "max_health": 80.0,
                    "max_mana":   50.0,
                    "mana_regen":  3.0,
                    "jumps":       2,
                },
                "offsets": {"right": -18, "left": -94, "y": -27},
                "animations": _SWORD_ANIMATIONS,
                "actions": {
                    "attack": {
                        "name": "Sword Slash Combo",
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
                        "damage": 30,
                        "mana_cost": 20,
                    },
                },
            },

            "morph": {
                "name": "Beast Morph",
                "stats": {
                    "max_health": 120.0,
                    "max_mana":    30.0,
                    "mana_regen":   2.0,
                    "jumps":        1,
                },
                "offsets": {"right": -23, "left": -89, "y": -26},
                "animations": _MORPH_ANIMATIONS,
                "actions": {
                    "attack": {
                        "name": "Beast Claw",
                        "damage": 12,
                        "mana_cost": 0,
                    },
                    "special": {
                        "name": "Primal Impact",
                        "damage": 20,
                        "mana_cost": 15,
                        "func": None,
                    },
                    "dash": {
                        "name": "Beast Dash",
                        "dash_speed": 220.0,
                        "mana_cost": 10,
                    },
                },
            },

            "mage": {
                "name": "Phase Mage",
                "stats": {
                    "max_health":  50.0,
                    "max_mana":    60.0,
                    "mana_regen":   3.5,
                    "jumps":        1,
                },
                "offsets": {"right": -29, "left": -83, "y": -25},
                "animations": _MAGE_ANIMATIONS,
                "actions": {
                    "attack": {
                        "name": "Arcane Bolt",
                        "damage": 18,
                        "mana_cost": 4,
                    },
                    "special": {
                        "name": "Infernal Flame Area",
                        "damage": 50,
                        "mana_cost": 28,
                        "is_aoe": True,
                        "duration": 1.2,
                    },
                },
            },
        },
    },

    "enemies": {
        "skeleton_sword": {
            "name":           "Skeleton Guard",
            "phase":          "green",
            "default_facing": "right",
            "hitbox":         {"width": 16, "height": 30},
            "render_offset":  {"x": -31, "y": -29},
            "stats": {
                "max_health":     45.0,
                "contact_damage": 12.0,
                "knockback_speed":  32.0,  
                "hit_duration":      0.50, 
                "death_duration":    1.50, 
            },
            "ai": {
                "walk_speed":      36.0,
                "patrol_dist":     80.0,
                "detect_range":   110.0,
                "attack_range":    28.0,
                "attack_reach":    34.0,
                "attack_timing":   (0.30, 0.50),
                "attack_duration": 0.60,
                "attack_cooldown": 1.5,
            },
            "animations": _SKELETON_SWORD_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Stab",
                    "damage":   12.0,
                    "reach":    34.0,
                    "timing":   (0.30, 0.50),
                    "duration": 0.60,
                },
                "attack2": {
                    "name":     "Overhead Slash",
                    "damage":   16.0,
                    "reach":    36.0,
                    "timing":   (0.35, 0.55),
                    "duration": 0.60,
                },
            },
        },

        "monster_eyes": {
            "name":           "Corrupted Creeper",
            "phase":          "red",
            "default_facing": "left",
            "hitbox":         {"width": 14, "height": 18},
            "render_offset":  {"x": -17, "y": -14},
            "stats": {
                "max_health":     25.0,
                "contact_damage": 10.0,
                "knockback_speed":  48.0,  
                "hit_duration":      0.30, 
                "death_duration":    1.00, 
            },
            "ai": {
                "walk_speed":      42.0,
                "patrol_dist":     80.0,
                "detect_range":    95.0,
                "attack_range":    24.0,
                "attack_reach":    28.0,
                "attack_timing":   (0.45, 0.60),
                "attack_duration": 0.80,
                "attack_cooldown": 1.5,
            },
            "animations": _MONSTER_EYES_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Bite",
                    "damage":   10.0,
                    "reach":    28.0,
                    "timing":   (0.45, 0.60),
                    "duration": 0.80,
                },
                "attack2": {
                    "name":     "Claw Rush",
                    "damage":   14.0,
                    "reach":    32.0,
                    "timing":   (0.50, 0.65),
                    "duration": 0.80,
                },
            },
        },

        "cultist_priest": {
            "name":           "Cultist Priest",
            "phase":          "red",
            "default_facing": "right",
            "hitbox":         {"width": 30, "height": 64},
            "render_offset":  {"x": -79, "y": -118},
            "stats": {
                "max_health":     120.0,
                "contact_damage":  14.0,
                "knockback_speed":  15.0,  
                "hit_duration":      0.20, 
                "death_duration":    2.00, 
            },
            "ai": {
                "walk_speed":      32.0,
                "patrol_dist":    100.0,
                "detect_range":   350.0,
                "attack_range":   320.0,
                "attack_reach":    20.0,
                "attack_timing":   (0.24, 0.48),
                "attack_duration": 0.75,
                "attack_cooldown": 2.4,
            },
            "animations": _CULTIST_PRIEST_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Void Casting",
                    "damage":   14.0,
                    "reach":    20.0,
                    "is_spell": True,
                    "timing":   (0.24, 0.48),
                    "duration": 0.75,
                    "func":     None,
                },
            },
        },

        "goblin": {
            "name":           "Goblin Scout",
            "phase":          "green",
            "default_facing": "right",
            "hitbox":         {"width": 16, "height": 18},
            "render_offset":  {"x": -24, "y": -26},
            "stats": {
                "max_health":     20.0,
                "contact_damage":  8.0,
                "knockback_speed":  64.0,  
                "hit_duration":      0.30, 
                "death_duration":    1.00, 
            },
            "ai": {
                "walk_speed":      48.0,
                "patrol_dist":     70.0,
                "detect_range":    90.0,
                "attack_range":    22.0,
                "attack_reach":    24.0,
                "attack_timing":   (0.30, 0.50),
                "attack_duration": 0.80,
                "attack_cooldown": 1.2,
            },
            "animations": _GOBLIN_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Dagger Slash",
                    "damage":    8.0,
                    "reach":    24.0,
                    "timing":   (0.30, 0.50),
                    "duration": 0.80,
                },
                "attack2": {
                    "name":     "Low Stab",
                    "damage":   12.0,
                    "reach":    26.0,
                    "timing":   (0.35, 0.55),
                    "duration": 0.80,
                },
            },
        },

        "big_monster": {
            "name":           "Root Golem",
            "phase":          "red",
            "default_facing": "right",
            "hitbox":         {"width": 32, "height": 38},
            "render_offset":  {"x": -24, "y": -17},
            "stats": {
                "max_health":     120.0,
                "contact_damage":  18.0,
                "knockback_speed":  15.0,  
                "hit_duration":      0.40, 
                "death_duration":    1.50, 
            },
            "ai": {
                "walk_speed":      30.0,
                "patrol_dist":    100.0,
                "detect_range":   160.0,
                "attack_range":   110.0,
                "attack_reach":    38.0,
                "attack_timing":   (0.80, 1.05),
                "attack_duration": 1.60,
                "attack_cooldown": 2.0,
            },
            "animations": _BIG_MONSTER_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Seismic Stomp",
                    "damage":   18.0,
                    "reach":    38.0,
                    "timing":   (0.80, 1.05),
                    "duration": 1.60,
                },
            },
        },

        "crown": {
            "name":           "Watcher Crow",
            "phase":          "green",
            "default_facing": "right",
            "hitbox":         {"width": 16, "height": 24},
            "render_offset":  {"x": -24, "y": -23},
            "stats": {
                "max_health":     18.0,
                "contact_damage":  7.0,
                "knockback_speed":  140.0,  
                "hit_duration":      0.25, 
                "death_duration":    0.80, 
            },
            "ai": {
                "walk_speed":      52.0,
                "patrol_dist":     80.0,
                "detect_range":    95.0,
                "attack_range":    22.0,
                "attack_reach":    26.0,
                "attack_timing":   (0.12, 0.32),
                "attack_duration": 0.55,
                "attack_cooldown": 1.2,
                "can_jump":        True,
                "jump_velocity":   -250.0,
            },
            "animations": _CROWN_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Peck",
                    "damage":    7.0,
                    "reach":    26.0,
                    "timing":   (0.12, 0.32),
                    "duration": 0.55,
                },
            },
        },

        "monster2": {
            "name":           "Shadow Lurker",
            "phase":          "green",
            "default_facing": "right",
            "hitbox":         {"width": 14, "height": 20},
            "render_offset":  {"x": -17, "y": -12},
            "stats": {
                "max_health":     40.0,
                "contact_damage": 10.0,
                "knockback_speed":  64.0,  
                "hit_duration":      0.30, 
                "death_duration":    1.00, 
            },
            "ai": {
                "walk_speed":      42.0,
                "patrol_dist":     85.0,
                "detect_range":   160.0,
                "attack_range":   130.0,
                "attack_reach":    26.0,
                "attack_timing":   (0.35, 0.55),
                "attack_duration": 0.80,
                "attack_cooldown": 1.5,
            },
            "animations": _MONSTER2_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Shadow Claw",
                    "damage":   10.0,
                    "reach":    20.0,
                    "timing":   (0.35, 0.55),
                    "duration": 0.80,
                },
                "attack2": {
                    "name":     "Plasma Gunshot",
                    "damage":   12.0,
                    "reach":    180.0,
                    "timing":   (0.35, 0.55),
                    "duration": 0.80,
                    "is_projectile": True,
                    "func":     None,
                },
            },
        },

        "monster3": {
            "name":           "Horned Imp",
            "phase":          "red",
            "default_facing": "right",
            "hitbox":         {"width": 18, "height": 24},
            "render_offset":  {"x": -23, "y": -24},
            "stats": {
                "max_health":     55.0,
                "contact_damage": 14.0,
                "knockback_speed":  64.0,  
                "hit_duration":      0.30, 
                "death_duration":    1.50, 
            },
            "ai": {
                "walk_speed":      38.0,
                "patrol_dist":     90.0,
                "detect_range":   110.0,
                "attack_range":    28.0,
                "attack_reach":    36.0,
                "attack_timing":   (0.27, 0.45),
                "attack_duration": 0.90,
                "attack_cooldown": 1.6,
            },
            "animations": _MONSTER3_ANIMATIONS,
            "actions": {
                "attack": {
                    "name":     "Gore",
                    "damage":   14.0,
                    "reach":    36.0,
                    "timing":   (0.27, 0.45),
                    "duration": 0.90,
                },
                "attack2": {
                    "name":     "Horn Charge",
                    "damage":   18.0,
                    "reach":    42.0,
                    "timing":   (0.35, 0.55),
                    "duration": 0.90,
                },
            },
        },
    },
}

ENTITY_DEFS["animations"] = {
    "player": {
        "sword": _SWORD_ANIMATIONS,
        "morph": _MORPH_ANIMATIONS,
        "mage":  _MAGE_ANIMATIONS,
    },
    "enemies": {
        key: data["animations"] for key, data in ENTITY_DEFS["enemies"].items()
    },
}

# Flat views for entity mapping

_BOSS_KEYS = {"cultist_priest"}

BOSS_DEFS: Dict[str, Any] = {
    k: v for k, v in ENTITY_DEFS["enemies"].items() if k in _BOSS_KEYS
}

ENEMY_DEFS: Dict[str, Any] = {
    k: v for k, v in ENTITY_DEFS["enemies"].items() if k not in _BOSS_KEYS
}
