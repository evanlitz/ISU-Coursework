# CS472 Project 2: Multi-Agent Pursuit-Evasion Game

A multi-agent game simulation implementing adversarial search algorithms for AI-based planning and decision-making. The game features three agents (Tom, Jerry, and Spike) engaged in a cyclical pursuit-evasion scenario on a 2D grid with obstacles.

## Game Overview

This project simulates a competitive multi-agent environment inspired by classic Tom and Jerry cartoons:

- **Tom** pursues Jerry
- **Jerry** evades Tom while pursuing Spike
- **Spike** evades Jerry while pursuing Tom

This creates a strategic cycle: Tom → Jerry → Spike → Tom

### Win Conditions

- **Tom wins**: Catches Jerry without being caught by Spike
- **Jerry wins**: Catches Spike without being caught by Tom
- **Spike wins**: Catches Tom without being caught by Jerry
- **Game ends**: When any agent wins, collides with an obstacle, or after 1000 iterations

### Scoring

- Winner: 3 points
- Non-collided agents: 1 point each
- Collided agents: 0 points

## Technical Implementation

### AI Algorithm

Each agent uses **Alpha-Beta Pruning** with a depth-2 search tree to make optimal decisions. The evaluation function considers:

- **Distance to target**: Primary objective using A* pathfinding
- **Distance from pursuer**: Defensive positioning using Manhattan distance
- **Danger penalty**: Quadratic penalty when too close to pursuer
- **Mobility**: Number of valid adjacent moves

### Game Environment

- **Grid Size**: 30x30
- **Grid Values**: 0 (free space), 1 (obstacle/wall)
- **Actions**: 9 possible moves per turn (stay, 4 cardinal, 4 diagonal)
- **State**: 3x2 array storing positions for all agents

## Project Structure

```
Project_2/
├── main.py                 # Core game engine and orchestration
├── devel.py               # Development/testing script
├── planners/
│   ├── tom.py             # Tom's AI agent implementation
│   ├── jerry.py           # Jerry's AI agent implementation
│   ├── spike.py           # Spike's AI agent implementation
│   └── planner.py         # Base planner utilities (A* helper)
├── data/
│   ├── grid_files/        # 100 grid environments (grid_0.npy - grid_99.npy)
│   └── proj_ii_solutions/ # Output directory for game trajectories
└── Project2_report.pdf    # Project report and analysis
```

## Requirements

- Python 3.7+
- NumPy
- Pandas

Install dependencies:
```bash
pip install numpy pandas
```

## Usage

### Run Full Test Suite

Executes all 100 grid scenarios, each run 5 times (500 total games):
```bash
python main.py
```

### Run Single Test

For development and debugging (tests grid 5, run 0):
```bash
python devel.py
```

## Output

Results are saved to `data/proj_ii_solutions/` as CSV files with naming convention:
```
[grid_id]_[run_id].csv
```

Each CSV contains the complete trajectory:
- `Tom_X`, `Tom_Y`: Tom's position over time
- `Jerry_X`, `Jerry_Y`: Jerry's position over time
- `Spike_X`, `Spike_Y`: Spike's position over time

## Agent Strategy Breakdown

| Agent | Primary Goal | Threat | Pursuit Weight | Evasion Weight |
|-------|-------------|--------|----------------|----------------|
| Tom   | Catch Jerry | Spike  | -3.0           | -1.2           |
| Jerry | Catch Spike | Tom    | -3.0           | 1.35           |
| Spike | Catch Tom   | Jerry  | -2.8           | 2.0            |

## Key Features

- **Adversarial Multi-Agent Search**: Implements game tree with alpha-beta pruning
- **A* Pathfinding**: Used for accurate distance estimation in heuristics
- **Collision Detection**: Validates moves against boundaries and obstacles
- **Comprehensive Logging**: Records complete game trajectories for analysis
- **Scalable Testing**: Handles 100 different grid configurations

## Author

Evan Litzer
Iowa State University
CS472 - Principles of Artificial Intelligence
