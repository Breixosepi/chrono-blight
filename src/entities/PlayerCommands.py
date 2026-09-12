from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerCommands:

    move_left:  bool = False
    move_right: bool = False
    run:        bool = False   
    jump:       bool = False   
    up:         bool = False
    attack:     bool = False   
    attack_special: bool = False 
    dash:       bool = False   
    parry:      bool = False
