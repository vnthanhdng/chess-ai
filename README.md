## Chess AI

A Python chess library and command-line engine for experimenting with search algorithms, evaluation functions, and simple reinforcement/puzzle workflows. The codebase is modular so you can run the CLI game or plug in different agent implementations for agent battling.

Team: Van Dang, Eli Jiang, Vivian Ma, Jaime Park
Course: CS 4260 - Fall 2025 - Vanderbilt University

### Highlights

- Search algorithms: Minimax, Minimax with alpha–beta pruning, Expectimax (in `src/search/`)
- Pluggable agents: human and search agents (see `src/agents/`)
- Evaluation: piece values + piece-square tables, with basic endgame awareness (`src/evaluation/`)
- Extra modules: puzzles, reinforcement experiments, simple tournament harnesses, and visualization helpers
- CLI for quick play and testing; small unit tests under `tests/`

## Requirements

- Python 3.9+ (tested locally)
- Dependencies are listed in `requirements.txt` (includes `python-chess`)

## Setup

Create a virtual environment and install the project dependencies:

```bash
# macOS / zsh example
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the CLI game

```bash
python main.py
```

The CLI is interactive. It will prompt for agent settings (engine depth, engine type, which side to play) depending on the configuration. You can enter moves in UCI (e.g., `e2e4`) or SAN (e.g., `e4`, `Nf3`).

During play you can use these commands:

- `moves` — list all legal moves
- `undo` — take back the last pair of moves (your move + engine reply)
- `help` — show command help
- `quit` — exit the game

## Running tests

There are lightweight unit tests in `tests/` to validate agents and evaluation. Run them with pytest (recommended):

```bash
pytest -q
```

You can also run the legacy test scripts directly:

```bash
python test_engine.py
python test_evaluation.py
```

## Project layout (key files)

- `main.py` — CLI entrypoint and interactive loop
- `engine.py` (legacy) — reference search implementations and helpers
- `evaluation.py` (legacy) — standalone evaluation function and piece-square tables
- `utils.py` — general helpers used by CLI and tests
- `src/agents/` — agent implementations (human, search-based agents, and learning agents)
- `src/search/` — search algorithm implementations (minimax, alphabeta, expectimax)
- `src/evaluation/` — modular evaluators and piece-square tables
- `tests/` — unit tests for agents, search, and evaluation

## License

This repository uses an MIT-style license. See `LICENSE` if included.


