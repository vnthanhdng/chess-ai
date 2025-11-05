from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.puzzles import PuzzleLoader, PuzzleEvaluator, load_sample_puzzles
from src.agents import AlphaBetaAgent
from src.evaluation import evaluate


def test_puzzle_loading():
    """Test that puzzles can be loaded."""
    print("\n" + "=" * 70)
    print("TEST 1: Loading Puzzles")
    print("=" * 70)
    
    sample_file = project_root / "data" / "sample_puzzles.csv"
    
    loader = PuzzleLoader(str(sample_file))
    puzzles = loader.load(limit=5)
    
    print(f"Loaded {len(puzzles)} puzzles")
    
    for puzzle in puzzles[:3]:
        print(f"  - {puzzle}")
    
    assert len(puzzles) == 5, "Should load 5 puzzles"
    print("\nTest 1 PASSED")


def test_puzzle_filtering():
    """Test puzzle filtering."""
    print("\n" + "=" * 70)
    print("TEST 2: Filtering Puzzles")
    print("=" * 70)
    
    sample_file = project_root / "data" / "sample_puzzles.csv"
    
    loader = PuzzleLoader(str(sample_file))
    
    # Test rating filter
    easy_puzzles = loader.load(max_rating=1500)
    print(f"Found {len(easy_puzzles)} puzzles with rating ≤ 1500")
    
    # Test theme filter
    mate_puzzles = loader.load(themes=['mateIn2'])
    print(f"Found {len(mate_puzzles)} mate-in-2 puzzles")
    
    if mate_puzzles:
        print(f"  Example: {mate_puzzles[0]}")
    
    print("\nTest 2 PASSED")


def test_puzzle_evaluation():
    """Test evaluating an agent on puzzles."""
    print("\n" + "=" * 70)
    print("TEST 3: Evaluating Agent")
    print("=" * 70)
    
    sample_file = project_root / "data" / "sample_puzzles.csv"
    
    # Load a few puzzles
    loader = PuzzleLoader(str(sample_file))
    puzzles = loader.load(limit=5)
    
    # Create agent
    agent = AlphaBetaAgent(evaluator=evaluate, depth=3, name="Test Agent")
    
    # Evaluate
    evaluator = PuzzleEvaluator(verbose=False)
    report = evaluator.evaluate(agent, puzzles, depth=3)

    print(f"  Evaluated {report.total_puzzles} puzzles")
    print(f"  Solved: {report.solved}/{report.total_puzzles} ({report.solve_rate:.1f}%)")
    print(f"  Avg time: {report.avg_time:.3f}s")
    print(f"  Avg nodes: {report.avg_nodes:,.0f}")
    
    assert report.total_puzzles == 5, "Should evaluate 5 puzzles"
    print("\nTest 3 PASSED")


def test_puzzle_board_setup():
    """Test that puzzle boards are set up correctly."""
    print("\n" + "=" * 70)
    print("TEST 4: Puzzle Board Setup")
    print("=" * 70)
    
    sample_file = project_root / "data" / "sample_puzzles.csv"
    
    loader = PuzzleLoader(str(sample_file))
    puzzles = loader.load(limit=1)
    puzzle = puzzles[0]
    
    print(f"Puzzle: {puzzle.puzzle_id}")
    print(f"FEN: {puzzle.fen}")
    print(f"Moves: {' '.join(puzzle.moves)}")
    
    board = puzzle.board
    print(f"\n Board set up successfully")
    print(f"  Turn: {'White' if board.turn else 'Black'}")
    print(f"  Legal moves: {board.legal_moves.count()}")
    
    # Verify the solution move is legal
    solution_move = puzzle.first_solution_move
    if solution_move:
        import chess
        move = chess.Move.from_uci(solution_move)
        assert move in board.legal_moves, "Solution move should be legal"
        print(f"  Solution move {solution_move} is legal")
    
    print("\nTest 4 PASSED")


def run_all_tests():
    """Run all puzzle system tests."""
    print("\n" + "=" * 70)
    print("RUNNING PUZZLE SYSTEM TESTS")
    print("=" * 70)
    
    try:
        test_puzzle_loading()
        test_puzzle_filtering()
        test_puzzle_evaluation()
        test_puzzle_board_setup()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED")
        print("=" * 70)
        print("\nThe puzzle system is working correctly!")
        print("\nSteps:")
        print("1. Download the full Lichess puzzle database from:")
        print("   https://database.lichess.org/#puzzles")
        print("\n2. Run evaluations:")
        print("   python scripts/solve_puzzles.py data/sample_puzzles.csv --limit 10")
        print("\n3. Compare algorithms:")
        print("   python scripts/solve_puzzles.py data/sample_puzzles.csv --compare")
        print("\n4. See PUZZLES.md for more examples")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()