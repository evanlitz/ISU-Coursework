import json
import mujoco as mj
import numpy as np
import multiprocessing as mp
from pathlib import Path
from generic_ik_solver import IKSolver

# cmd[3] == 1: gripper command. cmd[0] is the continuous value: 0.0 = fully open, 1.0 = fully closed.
GRIP = [1.0, 0.0, 0.0, 1]
RELEASE = [0.0, 0.0, 0.0, 1]

DROP_OFFSET = 0.01

_HERE = Path(__file__).resolve().parent
_SHARED_ROOT = (
    Path("/shared") if Path("/shared").exists() else _HERE.parent.parent / "shared"
)
_CALIB_PATH = _SHARED_ROOT / "calibrations" / "board_calibration.json"


class MotionPlanner(mp.Process):

    def __init__(self, trigger_pipe, output_pipe):
        super().__init__()

        if not _CALIB_PATH.exists():
            raise FileNotFoundError(
                f"Board calibration not found: {_CALIB_PATH}\n"
                "  → Run './run.sh docker-calibrate' to generate it."
            )

        with open(_CALIB_PATH) as f:
            calib = json.load(f)

        grip_shift = np.array(calib["a1grip"][:2]) - np.array(calib["a1"][:2])

        self._a1 = np.array(calib["a1"][:2]) + grip_shift
        self._h1 = np.array(calib["h1"][:2]) + grip_shift
        self._a8 = np.array(calib["a8"][:2]) + grip_shift
        self._h8 = np.array(calib["h8"][:2]) + grip_shift

        self._piece_heights = {
            "p": np.array(calib["pawn"][2]),
            "n": np.array(calib["knight"][2]),
            "b": np.array(calib["bishop"][2]),
            "r": np.array(calib["rook"][2]),
            "q": np.array(calib["queen"][2]),
            "k": np.array(calib["king"][2]),
        }
        self._piece_grips = {
            "p": 0.860273972603,
            "n": 0.6,
            "b": 0.712328767123,
            "r": 0.723287671233,
            "q": 0.690410958904,
            "k": 0.764383561644,
        }

        print(f"\nCalibration loaded from {_CALIB_PATH}")
        print(f"  a1={self._a1}  h1={self._h1}")
        print(f"  a8={self._a8}  h8={self._h8}\n")

        self.HOVER_Z = calib["hover"][2]
        self.LOWER_Z = calib["lower"][2]
        self.REST = calib["hover"][:2]

        self.trigger_pipe = trigger_pipe
        self.output_pipe = output_pipe
        self.daemon = True

    def _grip(self, piece: str):
        t = self._piece_grips[piece.lower()]
        return [t, 0.0, 0.0, 1.0]

    def tokenizeMove(self, move_string):
        parts = move_string.split("/")
        return {
            "from_sq": parts[0][:2],
            "to_sq": parts[0][2:],
            "moved_piece": parts[1],
            "captured_piece": parts[2] or None,
            "promotion_piece": parts[3] or None,
            "special": parts[4] or None,
        }

    def _remove_piece(self, square: str, piece: str) -> list:
        pos = self.get_board_position(square)
        return [
            RELEASE,
            pos + [self.HOVER_Z] + [0.0],  # approach above
            pos + [self.LOWER_Z] + [0.0],
            pos + [self.get_piece_height(piece)] + [0.0],  # lower and grip
            self._grip(piece),
            pos + [self.LOWER_Z] + [0.0],  # lift up
            pos + [self.HOVER_Z] + [0.0],
            self.REST + [self.HOVER_Z] + [0.0],  # move to rest above
            self.REST + [self.get_piece_height(piece) + DROP_OFFSET] + [0.0],  # lower to rest height
            RELEASE,
            self.REST + [self.HOVER_Z] + [0.0],  # return to rest
        ]

    def _move_piece(self, from_sq: str, to_sq: str, piece: str) -> list:
        from_pos = self.get_board_position(from_sq)
        to_pos = self.get_board_position(to_sq)
        # to_pos[0] -= 0.02
        return [
            RELEASE,
            from_pos + [self.HOVER_Z] + [0.0],  # approach above
            from_pos + [self.LOWER_Z] + [0.0],
            from_pos + [self.get_piece_height(piece)] + [0.0],  # lower and grip
            self._grip(piece),
            from_pos + [self.LOWER_Z] + [0.0],  # lift up
            from_pos + [self.HOVER_Z] + [0.0],
            to_pos + [self.HOVER_Z] + [0.0],  # move to target above
            to_pos + [self.LOWER_Z] + [0.0],
            to_pos + [self.get_piece_height(piece) + DROP_OFFSET] + [0.0],  # lower to target height
            RELEASE,
            to_pos + [self.LOWER_Z] + [0.0],
            to_pos + [self.HOVER_Z] + [0.0],
            self.REST + [self.HOVER_Z] + [0.0],  # return to rest
        ]

    def get_board_position(self, square) -> list:
        """
        Map a square name (e.g. 'e4') to [x, y] in MuJoCo world frame
        using bilinear interpolation between the 4 calibrated corners.

        Corner convention (looking down at board from above):
          a1 = (t_file=0, t_rank=0)   h1 = (t_file=1, t_rank=0)
          a8 = (t_file=0, t_rank=1)   h8 = (t_file=1, t_rank=1)
        """
        file_idx = ord(square[0]) - ord("a")  # 0 (a) … 7 (h)
        rank_idx = int(square[1]) - 1  # 0 (rank 1) … 7 (rank 8)

        t_f = file_idx / 7.0
        t_r = rank_idx / 7.0

        xy = (
            (1 - t_f) * (1 - t_r) * self._a1
            + t_f * (1 - t_r) * self._h1
            + (1 - t_f) * t_r * self._a8
            + t_f * t_r * self._h8
        )
        return [float(xy[0]), float(xy[1])]

    def get_piece_height(self, piece):
        return self._piece_heights[piece.lower()]

    def constructCommandsFromCmd(self, cmd: dict) -> list:
        """Build command sequence from a robot_commands.json dict."""
        from_sq = cmd["from_sq"]
        to_sq = cmd["to_sq"]
        piece = cmd["moved_piece"]
        captured = cmd.get("captured_piece")
        special = cmd.get("special")

        if special == "en_passant":
            cap_sq = to_sq[0] + from_sq[1]
            cap_piece = captured or ("p" if piece.isupper() else "P")
            return self._remove_piece(cap_sq, cap_piece) + self._move_piece(
                from_sq, to_sq, piece
            )
        elif special in ("castle_wk", "castle_bk"):
            rook = "R" if special == "castle_wk" else "r"
            rook_from, rook_to = (
                ("h1", "f1") if special == "castle_wk" else ("h8", "f8")
            )
            return self._move_piece(from_sq, to_sq, piece) + self._move_piece(
                rook_from, rook_to, rook
            )
        elif special in ("castle_wq", "castle_bq"):
            rook = "R" if special == "castle_wq" else "r"
            rook_from, rook_to = (
                ("a1", "d1") if special == "castle_wq" else ("a8", "d8")
            )
            return self._move_piece(from_sq, to_sq, piece) + self._move_piece(
                rook_from, rook_to, rook
            )
        elif captured:
            return self._remove_piece(to_sq, captured) + self._move_piece(
                from_sq, to_sq, piece
            )
        else:  # normal, promotion
            return self._move_piece(from_sq, to_sq, piece)

    def run(self):
        print("[Worker] Process started. Listening for triggers...")
        while True:
            try:
                signal = self.trigger_pipe.recv()
            except (EOFError, BrokenPipeError):
                # Parent closed the pipe (shutdown or crash)
                break
            if signal == "STOP":
                break

            print("Signal is:", signal)
            if isinstance(signal, dict):
                joint_commands = self.constructCommandsFromCmd(signal)
            else:
                # String format: "<from><to>/<piece>/<captured>/<promo>/<special>"
                joint_commands = self.constructCommandsFromCmd(
                    self.tokenizeMove(signal)
                )

            # Send results downstream
            try:
                self.output_pipe.send(joint_commands)
            except (EOFError, BrokenPipeError):
                # RunSim exited, pipe closed
                break
