## Chess

A small command-line chess engine written in Python. It plays against you as Black using minimax with alpha–beta pruning and a simple evaluation function based on piece values and piece-square tables.

Team: Van Dang, Eli Jiang, Vivian Ma, Jaime Park
Course: CS4260 - Artificial Intelligence
Vandebilt University

### Features

- Minimax search with optional alpha–beta pruning
- Heuristic evaluation in centipawns (material + piece-square tables, basic endgame awareness)
- Adjustable difficulty (search depth 2–5)
- Play from the terminal as White; engine moves as Black
- Handy commands during play: `moves`, `undo`, `help`, `quit`
- Simple test scripts for engine and evaluation

## Requirements

- Python 3.9+ (tested locally)
- Dependency: `python-chess`

## Setup

```bash
# (optional) create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install dependency
pip install python-chess
```

## Run the game

```bash
python main.py
```

You will be prompted to choose a difficulty (search depth). Enter moves in UCI (e.g., `e2e4`) or SAN (e.g., `e4`, `Nf3`) format.

During the game you can type:

- `moves` — list all legal moves
- `undo` — take back your last move and the engine’s reply
- `help` — show command help
- `quit` — exit the game

## Run tests

The project includes lightweight test scripts. Run them directly:

```bash
python test_evaluation.py
python test_engine.py
```

## Project structure

- `main.py` — CLI game loop and board printing
- `engine.py` — minimax and alpha–beta search (`find_best_move`, `find_best_move_alpha_beta`)
- `evaluation.py` — evaluation function with piece-square tables and basic endgame detection
- `utils.py` — helpers (placeholder)
- `test_engine.py` — engine behavior checks
- `test_evaluation.py` — evaluation function checks

## Notes

- Search depth heavily impacts strength and speed; higher depth means slower but stronger play.
- Evaluation is intentionally simple; feel free to tweak piece-square tables or add heuristics (mobility, king safety, pawn structure, etc.).

