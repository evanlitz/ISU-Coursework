#!/usr/bin/env python3
import argparse
import logging
import sys
import traceback
from pathlib import Path

from config import STARTING_FEN, HUMAN_COLOR, STOCKFISH_SKILL_LEVEL


def human_color_from_robot_color(robot_color: str) -> str:
    """Robot and human play opposite colors."""
    return "white" if robot_color == "black" else "black"

_ENGINE_DIR = Path(__file__).resolve().parent
_CRASH_LOG_PATH = _ENGINE_DIR / "last_crash.txt"
_ENGINE_LOG_PATH = _ENGINE_DIR / "engine_log.txt"


class Tee:
    """Write to both console and a file."""
    def __init__(self, stream, path: Path):
        self.stream = stream
        self.path = path
        self.file = open(path, "a", encoding="utf-8")

    def write(self, data):
        self.stream.write(data)
        self.file.write(data)
        self.file.flush()

    def flush(self):
        self.stream.flush()
        self.file.flush()

    def isatty(self):
        return self.stream.isatty()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Chess Robot Game Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  vision         Vision-driven game — reads camera, sends moves to robot (Demo 2)
  keyboard       Keyboard input — type UCI moves (Demo 1 style)
  robot_vs_robot Stockfish vs Stockfish — fully automatic

Examples:
  python main.py
  python main.py --mode keyboard
  python main.py --mode robot_vs_robot
  python main.py --skill 5 --verbose
        """
    )

    parser.add_argument(
        "--mode",
        choices=["vision", "keyboard", "robot_vs_robot"],
        default="vision",
        help="Game mode (default: vision)",
    )
    parser.add_argument(
        "--robot_color",
        choices=["white", "black"],
        default="black" if HUMAN_COLOR == "white" else "white",
        metavar="COLOR",
        help=(
            "Which color the robot plays; human is the other side "
            f"(default: opposite of config HUMAN_COLOR={HUMAN_COLOR!r})"
        ),
    )
    parser.add_argument(
        "--skill",
        type=int,
        default=STOCKFISH_SKILL_LEVEL,
        metavar="LEVEL",
        help=f"Stockfish skill level 1-20 (default: {STOCKFISH_SKILL_LEVEL})",
    )
    parser.add_argument(
        "--fen",
        default=STARTING_FEN,
        help="Starting FEN (ignored when --puzzle is set; puzzle uses camera only)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable DEBUG-level logging",
    )
    parser.add_argument(
        "--puzzle",
        dest="puzzle",
        action="store_true",
        default=True,
        help="Puzzle mode: board from camera only (default: on). Use --no-puzzle for --fen.",
    )
    parser.add_argument(
        "--no-puzzle",
        dest="puzzle",
        action="store_false",
        help="Disable puzzle mode; use --fen for starting position.",
    )
    parser.add_argument(
        "--to_move",
        choices=["auto", "white", "black"],
        default="auto",
        metavar="WHO",
        help=(
            "Puzzle only: side to move in the position (white/black). "
            "auto = infer from human's color (opposite of --robot_color). Ignored without --puzzle."
        ),
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Skip interactive prompts (for use when launched by the main orchestrator)",
    )

    return parser.parse_args()


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    root = logging.getLogger()
    root.setLevel(level)
    sh = logging.StreamHandler(sys.stdout)  # stdout is Tee'd to engine_log.txt
    sh.setLevel(level)
    sh.setFormatter(fmt)
    root.addHandler(sh)
    return logging.getLogger("main")


def run_vision_mode(args, logger):
    from game_loop import GameLoop

    human_color = human_color_from_robot_color(args.robot_color)

    print()
    print("=" * 55)
    print("  CHESS ROBOT — Vision Mode (Demo 2)")
    print(
        f"  Human: {human_color.upper()}   Robot: {args.robot_color.upper()}"
    )
    print(f"  Stockfish skill: {args.skill}/20")
    if args.puzzle:
        print("  Puzzle: position from camera — side to move from --to_move (or auto)")
    else:
        print(f"  Starting FEN: {args.fen}")
    print("=" * 55)
    print()
    if not args.auto:
        print("  Make sure the vision module is running:")
        print("    cd Backend/vision_module && python run.py")
        print()
        input("  Press ENTER when vision module is ready...")
        print()

    import config
    config.STOCKFISH_SKILL_LEVEL = args.skill

    loop = GameLoop(
        starting_fen=None if args.puzzle else args.fen,
        human_color=human_color,
        puzzle_mode=args.puzzle,
        to_move=args.to_move,
    )
    loop.setup()
    loop.run()
    loop.shutdown()


def run_keyboard_mode(args, logger):
    import human_vs_robot

    hc = human_color_from_robot_color(args.robot_color)

    print()
    print("=" * 55)
    print("  CHESS ROBOT — Keyboard Mode (Demo 1 Style)")
    print(f"  Human: {hc.upper()}   Robot: {args.robot_color.upper()}")
    print(f"  Stockfish skill: {args.skill}/20")
    print("=" * 55)
    print()

    import config
    config.STOCKFISH_SKILL_LEVEL = args.skill
    config.STARTING_FEN = args.fen
    config.HUMAN_COLOR = human_color_from_robot_color(args.robot_color)
    human_vs_robot.main()


def run_robot_vs_robot(args, logger):
    import robot_vs_robot

    print()
    print("=" * 55)
    print("  CHESS ROBOT — Robot vs Robot")
    print("=" * 55)
    print()

    robot_vs_robot.main()


def main():
    args = parse_args()
    # Tee stdout/stderr to engine_log.txt so all console output is also saved
    try:
        sys.stdout = Tee(sys.stdout, _ENGINE_LOG_PATH)
        sys.stderr = Tee(sys.stderr, _ENGINE_LOG_PATH)
    except OSError:
        pass
    logger = setup_logging(verbose=args.verbose)

    logger.info(
        f"Starting: mode={args.mode}, robot_color={args.robot_color}, "
        f"puzzle={args.puzzle}, skill={args.skill}"
    )

    try:
        if args.mode == "vision":
            run_vision_mode(args, logger)
        elif args.mode == "keyboard":
            run_keyboard_mode(args, logger)
        elif args.mode == "robot_vs_robot":
            run_robot_vs_robot(args, logger)

    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye.")
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"\n  Fatal error: {e}")
        try:
            with open(_CRASH_LOG_PATH, "w") as f:
                f.write(traceback.format_exc())
            print(f"  Traceback saved to: {_CRASH_LOG_PATH}")
        except OSError:
            pass
        sys.exit(1)

    print("\n  Session complete.")


if __name__ == "__main__":
    main()
