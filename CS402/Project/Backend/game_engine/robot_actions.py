from dataclasses import dataclass
from enum import Enum


class RobotAction(Enum):
    PICK_UP = "pick_up"
    PLACE_DOWN = "place_down"
    MOVE_TO_GRAVEYARD = "graveyard"
    MOVE_TO = "move_to"
    HOME = "home"
    OPEN_GRIPPER = "open_gripper"
    CLOSE_GRIPPER = "close_gripper"

@dataclass
class RobotStep:
    action: RobotAction
    square: str
    piece: str
    description: str

