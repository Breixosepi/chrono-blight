# src/states/entity/player/__init__.py
from src.states.entity.player.IdleState import IdleState
from src.states.entity.player.WalkState import WalkState
from src.states.entity.player.JumpState import JumpState
from src.states.entity.player.FallState import FallState
from src.states.entity.player.DashState import DashState
from src.states.entity.player.AttackState import AttackState
from src.states.entity.player.AttackSpecialState import AttackSpecialState
from src.states.entity.player.HitState import HitState
from src.states.entity.player.DeathState import DeathState

PlayerIdleState = IdleState
PlayerWalkState = WalkState
PlayerAirborneState = FallState
PlayerDashState = DashState
PlayerAttackState = AttackState
PlayerAttackSpecialState = AttackSpecialState
PlayerHitState = HitState
PlayerDeathState = DeathState

__all__ = [
    "IdleState",
    "WalkState",
    "JumpState",
    "FallState",
    "DashState",
    "AttackState",
    "AttackSpecialState",
    "HitState",
    "DeathState",
    "PlayerIdleState",
    "PlayerWalkState",
    "PlayerAirborneState",
    "PlayerDashState",
    "PlayerAttackState",
    "PlayerAttackSpecialState",
    "PlayerHitState",
    "PlayerDeathState",
]
