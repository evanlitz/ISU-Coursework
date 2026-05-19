# Game Engine

Chess game engine that integrates Stockfish, vision-based move detection, game state management, and robot action planning.

## Setup

### 1. Python Virtual Environment

```bash
cd Backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Stockfish

Download the Stockfish executable:
- **Windows**: https://stockfishchess.org/download/ — download the `.exe` file
- **macOS**: `brew install stockfish`
- **Linux**: `sudo apt install stockfish`

Then add your path to `config.py`:

```python
STOCKFISH_PATHS = [
    "stockfish",
    "stockfish.exe",
    r"C:\path\to\your\stockfish.exe",  # <-- update this
]
```

The engine searches these paths in order and uses the first one found.

### 4. Configuration

Key settings in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `STOCKFISH_SKILL_LEVEL` | `20` | Engine strength (1–20) |
| `STOCKFISH_TIME_LIMIT` | `2.0` | Seconds per move |
| `HUMAN_COLOR` | `"white"` | Which side the human plays |
| `VISION_STABILITY_MODE` | `"per_square"` | Stability filter mode (`per_square`, `majority`, `strict`) |
| `VISION_STABILITY_WINDOW` | `5` | Sliding window size (frames) |
| `VISION_STABILITY_REQUIRED` | `3` | Votes required within the window |
| `VISION_POLL_INTERVAL` | `0.4` | Seconds between vision reads |
| `VISION_MIN_STABLE_SECONDS` | `0.7` | Minimum dwell time before a FEN is accepted |
| `VISION_CONFIDENCE_MIN` | `0.6` | YOLO confidence below this signals a hand over the board |
| `VISION_RECOVERY_FRAMES` | `3` | Clean frames required after a hand withdraws |

## Running

From the `Backend` directory with the venv activated:

```bash
# Vision mode — reads camera, sends moves to robot (default)
python game_engine/main.py

# Keyboard mode — type UCI moves manually (testing)
python game_engine/main.py --mode keyboard

# Robot vs Robot — Stockfish plays both sides automatically
python game_engine/main.py --mode robot_vs_robot

# Puzzle mode — starting position from camera, not standard start
python game_engine/main.py --puzzle

# Set Stockfish skill level and verbose logging
python game_engine/main.py --skill 5 --verbose
```

Make sure the vision module is running before starting vision mode:

```bash
cd Backend/vision_module && python run.py
```

## Arguments

| Argument | Values | Default | Description |
|---|---|---|---|
| `--mode` | `vision`, `keyboard`, `robot_vs_robot` | `vision` | Game mode |
| `--robot_color` | `white`, `black` | opposite of `HUMAN_COLOR` in config | Which color the robot plays; human plays the other side |
| `--skill` | `1`–`20` | `STOCKFISH_SKILL_LEVEL` in config | Stockfish difficulty |
| `--fen` | any valid FEN string | standard starting position | Starting board position (ignored in puzzle mode) |
| `--puzzle` / `--no-puzzle` | — | `--puzzle` on | Puzzle mode: read starting position from camera instead of `--fen` |
| `--to_move` | `auto`, `white`, `black` | `auto` | Puzzle mode only: which side has the move in the detected position. `auto` infers from `--robot_color` (human moves first unless robot is white) |
| `--verbose` / `-v` | — | off | Enable DEBUG-level logging |
| `--auto` | — | off | Skip interactive prompts; use when launched by the main orchestrator |

### Examples

```bash
# Human plays black, robot plays white, skill 10
python game_engine/main.py --robot_color white --skill 10

# Puzzle mode: camera reads the board, black to move
python game_engine/main.py --puzzle --to_move black

# Start from a custom position (non-puzzle)
python game_engine/main.py --no-puzzle --fen "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"

# Robot vs Robot, max skill, verbose output
python game_engine/main.py --mode robot_vs_robot --skill 20 --verbose
```

## Module Overview

| File | Purpose |
|---|---|
| `main.py` | Entry point; argument parsing, mode dispatch, logging setup |
| `game_loop.py` | Main 20 Hz event loop; coordinates all subsystems |
| `game_state.py` | State machine (`IDLE`, `WAITING_FOR_OPPONENT`, `ROBOT_THINKING`, `ROBOT_MOVING`, `GAME_OVER`) and `TurnManager` |
| `board_state.py` | Board position tracking via python-chess |
| `move_detector.py` | Infers moves from before/after FEN positions |
| `move_validator.py` | Validates and classifies moves (normal, capture, castling, en passant, promotion) |
| `stockfish_engine.py` | Stockfish subprocess wrapper (UCI protocol) |
| `game_over_detector.py` | Detects checkmate, stalemate, and draws |
| `fen_stability.py` | Per-square voting stability filter for raw vision output |
| `fen_history.py` | Confirmed/pending position history; tiebreaker for close votes |
| `fen_utils.py` | FEN structural and semantic validation, position comparison |
| `fen_reader.py` | Reads latest FEN from the vision module output file |
| `vision_interface.py` | Wraps `fen_reader` and `fen_stability` into a single polling interface |
| `robot_interface.py` | Writes JSON move commands for the robot planner |
| `robot_planner.py` | Converts classified move info into a robot command dict |
| `robot_actions.py` | Robot action type definitions |
| `config.py` | All configuration and paths |
| `human_vs_robot.py` | Keyboard mode game driver |
| `robot_vs_robot.py` | Robot vs robot mode game driver |
| `sys_check.py` | Pre-flight checks (Stockfish path, vision module, dependencies) |
| `test_vision_pipeline.py` | Manual test script for the vision stability pipeline |
