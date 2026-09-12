"""
Chrono Blight
"""

from gale.command import Command


class MoveLeftCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_direction = -1


class MoveRightCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_direction = 1


class StopMoveLeftCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        if receiver.move_direction < 0:
            receiver.move_direction = 0


class StopMoveRightCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        if receiver.move_direction > 0:
            receiver.move_direction = 0


class MoveUpCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_looking_up = True


class StopMoveUpCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_looking_up = False


class JumpCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.jump_requested = True
        receiver.jump_held = True


class StopJumpCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.jump_held = False


class RunCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_running = True


class StopRunCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_running = False


class AttackCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.attack_requested = True


class AttackSpecialCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.special_attack_requested = True


class DashCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.dash_requested = True


MOVE_LEFT = MoveLeftCommand()
STOP_MOVE_LEFT = StopMoveLeftCommand()
MOVE_RIGHT = MoveRightCommand()
STOP_MOVE_RIGHT = StopMoveRightCommand()
MOVE_UP = MoveUpCommand()
STOP_MOVE_UP = StopMoveUpCommand()
JUMP = JumpCommand()
STOP_JUMP = StopJumpCommand()
RUN = RunCommand()
STOP_RUN = StopRunCommand()
ATTACK = AttackCommand()
ATTACK_SPECIAL = AttackSpecialCommand()
DASH = DashCommand()

