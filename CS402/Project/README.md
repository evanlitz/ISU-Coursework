# ug_hf_1

Integrated stack for **camera-based chess board perception**, **game logic**, and **robot / simulation control** (ISU COM S senior design).

This repository is organized by role. Use the sections below to find where to run things; **subfolder READMEs** are linked where they exist.

The Final Demo Video can be found with the link below:
https://youtu.be/dqPGt-fecFE?si=bK0mOEL9zTEeLaWg
---

## Quick navigation — documentation in this repo

| Document                                                                           | Description                                                                                     |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [Backend/vision_module/README.md](Backend/vision_module/README.md)                 | Chess vision: camera, calibration, live detection, FEN output, integration with the game engine |
| [Backend/vision_module/TRAINING_GUIDE.md](Backend/vision_module/TRAINING_GUIDE.md) | Training the per-square piece classifier (data capture, folders, training script)               |
| [Backend/game_engine/README](Backend/game_engine/README)                           | Chess game engine: Stockfish, move validation, game state, robot planning                       |
| [Backend/deploy_mujoco/README.md](Backend/deploy_mujoco/README.md)                 | UR10e + MuJoCo demos (FK/IK, gripper)                                                           |

Other areas (`planner`, `Frontend`) are summarized below where there is no dedicated README.

---

## Top-level layout

| Folder                   | Role                                                                |
| ------------------------ | ------------------------------------------------------------------- |
| [Backend/](Backend/)     | Python backend: vision, chess engine, simulation, planning snippets |
| [Documents/](Documents/) | Team documents (placeholders / shared materials)                    |
| [Frontend/](Frontend/)   | Frontend or demo assets (structure may vary by branch)              |

---

## Backend

### `Backend/vision_module/` — computer vision

**What it does:** Captures video, uses saved **board homography** and optional **camera calibration**, warps to a bird’s-eye board view, classifies **64 squares** with a PyTorch model, and emits **FEN** and **`gameplay_data/latest_frame_data.json`** for downstream code.

**Entry point:** `run.py` (live mode, calibration, headless option, etc.).

**Docs:** [README](Backend/vision_module/README.md) · [Training guide](Backend/vision_module/TRAINING_GUIDE.md)

---

### `Backend/game_engine/` — chess game loop and robot bridge

**What it does:** Integrates **Stockfish**, **move validation**, **game state**, **vision/FEN input**, and **robot action planning**. Orchestrates modes such as vision-driven play, keyboard moves, and automated play.

**Canonical copy:** [Backend/game_engine/README](Backend/game_engine/README)

#### Python environment

From the `Backend` directory:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Install dependencies

```bash
pip install python-chess numpy
# OR
cd game_engine
pip install -r requirements.txt
```

For a focused install you can use [Backend/game_engine/requirements.txt](Backend/game_engine/requirements.txt) from that directory.

#### Stockfish

- **Windows:** [stockfishchess.org/download](https://stockfishchess.org/download/)
- **macOS:** `brew install stockfish`
- **Linux:** `sudo apt install stockfish`

Point the engine at your binary in `Backend/game_engine/config.py`:

```python
STOCKFISH_PATHS = [
    "stockfish",
    "stockfish.exe",
    r"C:\path\to\your\stockfish.exe",  # <-- update this
]
```

The engine tries these paths in order. If `stockfish` is on `PATH`, the first entry usually suffices.

#### Configuration (`config.py`)

| Setting                 | Default   | Description                |
| ----------------------- | --------- | -------------------------- |
| `STOCKFISH_SKILL_LEVEL` | `20`      | Engine strength (1–20)     |
| `STOCKFISH_TIME_LIMIT`  | `2.0`     | Seconds per move           |
| `HUMAN_COLOR`           | `"white"` | Which side the human plays |

#### Running

From `Backend` with the venv active, the original README suggested:

```bash
python demo_game_loop.py      # human vs Stockfish (text)
python demo_robot_vs_robot.py # Stockfish vs Stockfish
```

Those filenames may not exist in this repo; use the CLI under `game_engine` instead:

```bash
cd game_engine
python main.py --mode keyboard
python main.py --mode robot_vs_robot
python main.py --mode vision
```

Run `python main.py --help` for current options.

#### Module overview

| File                    | Purpose                                                            |
| ----------------------- | ------------------------------------------------------------------ |
| `board_state.py`        | Board position tracking via python-chess                           |
| `config.py`             | Configuration and paths                                            |
| `fen_utils.py`          | FEN validation and position comparison                             |
| `game_state.py`         | State machine (IDLE, WAITING, THINKING, MOVING, GAME_OVER)         |
| `game_over_detector.py` | Checkmate, stalemate, draws                                        |
| `move_detector.py`      | Infers moves from before/after FEN                                 |
| `move_validator.py`     | Validates moves (normal, capture, castling, en passant, promotion) |
| `robot_actions.py`      | Robot action type definitions                                      |
| `robot_planner.py`      | Classified moves → robot action plans                              |
| `stockfish_engine.py`   | Stockfish subprocess (UCI)                                         |

---

### `Backend/deploy_mujoco/` — UR10e MuJoCo simulation

**What it does:** Demo scripts for **forward/inverse kinematics** and **gripper** control in MuJoCo for a UR10e model.

**Docs:** [README](Backend/deploy_mujoco/README.md)

---

### `Backend/planner/` — planning utilities

**What it contains:** Extra planning/control scripts (e.g. IK-related `deploy_ik.py` alongside the main MuJoCo demo folder). Treat as supporting code unless your workflow depends on it.

**Docs:** No README; see files in that directory.

---

## Documents

Shared reports, figures, or design notes can live under [Documents/](Documents/). Add an index file there if the set grows.

---

## Frontend

Web or demo UI assets under [Frontend/](Frontend/). If your branch adds apps (e.g. React), document setup in a `Frontend/README.md` when needed.

---

## Contributing pointers

- **Vision changes:** see [Backend/vision_module/README.md](Backend/vision_module/README.md) and requirements in `Backend/vision_module/requirements.txt`.
- **Game engine changes:** see [Backend/game_engine/README](Backend/game_engine/README) and `python main.py --help`.
- **Simulation / arm:** see [Backend/deploy_mujoco/README.md](Backend/deploy_mujoco/README.md).
