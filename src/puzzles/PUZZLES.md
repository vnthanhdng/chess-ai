# Puzzles Module

## Overview

The puzzle module provides us a system for evaluating chess AI agents using tactical puzzles from the Lichess database. This allows us to test how well your agents can find the best move in specific tactical positions.

## Quick Start

```python
from src.puzzles import PuzzleLoader, PuzzleEvaluator, load_sample_puzzles
from src.agents import AlphaBetaAgent

# Load puzzles
loader = PuzzleLoader("data/puzzles.csv")
puzzles = loader.load(min_rating=1200, max_rating=1600, limit=50)

# Evaluate an agent
agent = AlphaBetaAgent(depth=4)
evaluator = PuzzleEvaluator()
report = evaluator.evaluate(agent, puzzles)

# View results
report.print_summary()
report.print_detailed(show_failed_only=True)
```


## Module Components


### 1. Puzzle (`puzzle.py`)

Represents a single chess puzzle with all its metadata.

### 1. Puzzle (`puzzle.py`)

Represents a single chess puzzle with all its metadata.

**Key Attributes:**
- `puzzle_id`: Unique identifier
- `fen`: Starting position (before setup move)
- `moves`: List of moves in UCI format (first move is opponent's setup, rest are solution)
- `rating`: Difficulty rating (similar to chess Elo)
- `themes`: List of tactical themes (e.g., "fork", "pin", "mateIn2")
- `solution_moves`: Property that returns just the solution (excludes setup move)
- `first_solution_move`: Property for the correct first move
- `board`: Property that returns the chess.Board after the setup move is applied

**Important Methods:**
```python
puzzle = puzzles[0]
print(puzzle.board)  # Board ready for the agent to solve
print(puzzle.first_solution_move)  # The correct answer
print(puzzle.has_theme("fork"))  # Check for specific themes
```

### 2. PuzzleLoader (`puzzle_loader.py`)

Loads and filters puzzles from the Lichess CSV database.

**Basic Usage:**
```python
loader = PuzzleLoader("data/puzzles.csv")

# Load with filters
puzzles = loader.load(
    min_rating=1200,      # Minimum difficulty
    max_rating=1800,      # Maximum difficulty
    themes=["fork"],      # Must include these themes
    limit=100             # Max number to load
)

# Get database statistics
stats = loader.get_stats()
print(f"Total puzzles: {stats['total_puzzles']}")
print(f"Rating range: {stats['min_rating']} - {stats['max_rating']}")
print(f"Available themes: {stats['unique_themes']}")
```

**Custom Filtering:**
```python
# Load only mate-in-2 puzzles with high popularity
puzzles = loader.load(
    themes=["mateIn2"],
    custom_filter=lambda p: p.popularity > 90,
    limit=50
)
```

### 3. PuzzleEvaluator (`puzzle_evaluator.py`)

Evaluates agents on puzzle sets and generates detailed reports.

**Single Agent Evaluation:**
```python
evaluator = PuzzleEvaluator(verbose=True)
report = evaluator.evaluate(
    agent=my_agent,
    puzzles=puzzles,
    depth=4  # Override agent's default depth (optional)
)

# Access report data
print(f"Solve rate: {report.solve_rate:.1f}%")
print(f"Average time: {report.avg_time:.3f}s")
print(f"Average nodes: {report.avg_nodes:,.0f}")
```

**Compare Multiple Agents:**
```python
agents = [
    MinimaxAgent(depth=3),
    AlphaBetaAgent(depth=3),
    AlphaBetaAgent(depth=4)
]

reports = evaluator.compare_agents(agents, puzzles, depth=3)
```

### 4. Results and Reports

**PuzzleResult** - Individual puzzle attempt:
```python
result = report.results[0]
print(result.solved)           # True/False
print(result.agent_move)       # Agent's move in UCI
print(result.correct_move)     # Correct move in UCI
print(result.nodes_searched)   # Nodes searched for this puzzle
print(result.time_taken)       # Time in seconds
```

**EvaluationReport** - Complete evaluation summary:
```python
# Print formatted summaries
report.print_summary()           # Overall statistics
report.print_detailed()          # All puzzle results
report.print_detailed(show_failed_only=True)  # Only failures

# Filter reports by criteria
easy_puzzles = report.by_rating_range(1000, 1400)
fork_puzzles = report.by_theme("fork")

# Access raw data
for result in report.results:
    if not result.solved:
        print(f"Failed {result.puzzle.puzzle_id}: {result.puzzle.rating}")
```

## Common Use Cases

### 1. Testing Agent Tactical Strength

```python
# Test on progressively harder puzzles
loader = PuzzleLoader("data/puzzles.csv")
agent = AlphaBetaAgent(depth=4)
evaluator = PuzzleEvaluator()

for min_r, max_r in [(1000, 1200), (1200, 1400), (1400, 1600)]:
    puzzles = loader.load(min_rating=min_r, max_rating=max_r, limit=50)
    report = evaluator.evaluate(agent, puzzles)
    print(f"Rating {min_r}-{max_r}: {report.solve_rate:.1f}% solved")
```

### 2. Finding Agent Weaknesses

```python
# Test on specific tactical themes
themes_to_test = ["fork", "pin", "skewer", "discoveredAttack", "mateIn2"]

for theme in themes_to_test:
    puzzles = loader.load(themes=[theme], limit=30)
    report = evaluator.evaluate(agent, puzzles)
    print(f"{theme}: {report.solve_rate:.1f}% solve rate")
```

### 3. Depth Analysis

```python
# Compare different search depths
agent = AlphaBetaAgent()
puzzles = loader.load(min_rating=1400, max_rating=1600, limit=50)

for depth in [2, 3, 4, 5]:
    report = evaluator.evaluate(agent, puzzles, depth=depth)
    print(f"Depth {depth}: {report.solve_rate:.1f}% "
          f"({report.avg_time:.3f}s avg, {report.avg_nodes:,.0f} nodes)")
```

### 4. Performance Profiling

```python
# Identify slow puzzles
report = evaluator.evaluate(agent, puzzles)
slow_puzzles = sorted(report.results, key=lambda r: r.time_taken, reverse=True)

print("Slowest puzzles:")
for result in slow_puzzles[:10]:
    print(f"  {result.puzzle.puzzle_id}: {result.time_taken:.3f}s, "
          f"{result.nodes_searched:,} nodes")
```

## Puzzle CSV Format

The Lichess puzzle database CSV has these columns:
- `PuzzleId`: Unique identifier (e.g., "00008")
- `FEN`: Position before setup move
- `Moves`: Space-separated UCI moves (setup move + solution)
- `Rating`: Difficulty rating (500-3000)
- `RatingDeviation`: Uncertainty in rating
- `Popularity`: Popularity score (-100 to 100)
- `NbPlays`: Number of times played
- `Themes`: Space-separated theme tags
- `GameUrl`: Link to original game on Lichess

## Understanding Puzzle Flow

1. **Initial FEN**: The starting position
2. **Setup Move** (moves[0]): Opponent's last move that creates the tactical opportunity
3. **Solution Moves** (moves[1:]): The winning sequence
4. **Agent Task**: Find `first_solution_move` from the board after setup move

```python
puzzle = puzzles[0]
# The board property automatically applies the setup move
board = puzzle.board  # Ready for agent to solve
correct = puzzle.first_solution_move  # What the agent should find
```

## Integration with Agents

All agents inheriting from `BaseAgent` work automatically with the puzzle system:

```python
# The evaluator calls agent.choose_move(board) for each puzzle
# It tracks nodes_searched automatically via the BaseAgent interface
# No special puzzle-specific code needed in your agent!

class MyCustomAgent(BaseAgent):
    def choose_move(self, board: chess.Board) -> chess.Move:
        # Your implementation
        # Just return the best move you find
        return best_move

# It just works!
agent = MyCustomAgent()
report = evaluator.evaluate(agent, puzzles)
```

### Performance Considerations
- Start with small puzzle sets (10-50) for initial testing
- Use `limit` parameter to avoid loading entire database
- Higher rated puzzles (1800+) may require deeper search
- Monitor `nodes_searched` to understand computational cost

### Meaningful Evaluation
- Use at least 50 puzzles per rating range for statistical significance
- Test across multiple rating ranges to see agent strengths/weaknesses
- Consider theme-specific testing to identify tactical blind spots
- Compare agents on the same puzzle set for fair comparison

### Debugging Failed Puzzles
```python
# When puzzles fail, examine them manually
report = evaluator.evaluate(agent, puzzles)

for result in report.results:
    if not result.solved:
        print(f"\nFailed: {result.puzzle}")
        print(f"FEN: {result.puzzle.fen}")
        print(f"Correct: {result.correct_move}")
        print(f"Agent chose: {result.agent_move}")
        print(result.puzzle.board)  # Visual board representation
```

### Memory Management
```python
# For large experiments, load puzzles in batches
def batch_evaluate(agent, loader, rating_ranges, batch_size=100):
    all_reports = []
    for min_r, max_r in rating_ranges:
        puzzles = loader.load(min_rating=min_r, max_rating=max_r, 
                             limit=batch_size)
        report = evaluator.evaluate(agent, puzzles)
        all_reports.append(report)
    return all_reports
```

## Common Themes in Puzzle Database

Frequent tactical themes you'll encounter:
- `mateIn1`, `mateIn2`, `mateIn3`: Forced checkmate sequences
- `fork`: Attack multiple pieces simultaneously
- `pin`: Piece cannot move without exposing higher value piece
- `skewer`: Forcing high-value piece to move, exposing lower-value piece behind it
- `discoveredAttack`: Moving piece reveals attack from another piece
- `deflection`: Forcing piece away from key square/defense
- `sacrifice`: Giving up material for tactical advantage
- `hangingPiece`: Opponent left piece undefended
- `short`: Puzzle has short solution (good for testing)
- `endgame`: Endgame position


## Running Experiments 

Coming soon!