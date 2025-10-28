"""Tests for search algorithms."""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import chess
from src.search import MiniMaxSearch, AlphaBetaSearch, ExpectimaxSearch
from src.evaluation import evaluate


def test_finds_mate_in_one():
    """Search should find mate in one."""
    board = chess.Board()
    board.set_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
    
    search = MiniMaxSearch(evaluate)
    move, score = search.search(board, depth=2)
    
    assert move.uci() == "h5f7", f"Should find Qxf7#, got {move}"
    print("Finds mate in one")


def test_alphabeta_equals_minimax():
    """Alpha-beta should return same evaluation as minimax."""
    board = chess.Board()
    
    minimax = MiniMaxSearch(evaluate)
    alphabeta = AlphaBetaSearch(evaluate)
    
    _, minimax_score = minimax.search(board, depth=3)
    _, alphabeta_score = alphabeta.search(board, depth=3)
    
    assert minimax_score == alphabeta_score, \
        f"Scores should match: {minimax_score} vs {alphabeta_score}"
    print("Alpha-beta equals minimax")


def test_alphabeta_prunes():
    """Alpha-beta should search fewer nodes than minimax."""
    board = chess.Board()
    
    minimax = MiniMaxSearch(evaluate)
    alphabeta = AlphaBetaSearch(evaluate)
    
    minimax.search(board, depth=3)
    alphabeta.search(board, depth=3)
    
    assert alphabeta.nodes_searched < minimax.nodes_searched, \
        f"Alpha-beta should prune: {alphabeta.nodes_searched} vs {minimax.nodes_searched}"
    print(f"Alpha-beta prunes (searched {alphabeta.nodes_searched}/{minimax.nodes_searched} nodes)")


def test_captures_hanging_piece():
    """Should capture free pieces."""
    board = chess.Board()
    board.set_fen("rnb1kbnr/pppp1ppp/8/3q4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    
    search = AlphaBetaSearch(evaluate)
    move, _ = search.search(board, depth=2)
    
    assert move.uci() == "d1d5" or board.piece_at(move.to_square), \
        "Should capture queen"
    print("Captures hanging piece")

# EXPECTIMAX TESTS
def test_expectimax_finds_forced_mate():
    """Expectimax should find forced checkmate."""
    board = chess.Board()
    board.set_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
    
    search = ExpectimaxSearch(evaluate)
    move, score = search.search(board, depth=2)
    
    assert move.uci() == "h5f7", f"Should find Qxf7#, got {move}"
    print("Expectimax finds mate in one")


def test_expectimax_differs_from_minimax():
    """Expectimax should give different scores than minimax (expected vs worst-case)."""
    board = chess.Board()
    
    minimax = MiniMaxSearch(evaluate)
    expectimax = ExpectimaxSearch(evaluate)
    
    _, minimax_score = minimax.search(board, depth=3)
    _, expectimax_score = expectimax.search(board, depth=3)
    
    # Scores should differ because expectimax assumes random play
    assert minimax_score != expectimax_score, \
        f"Scores should differ: minimax={minimax_score} vs expectimax={expectimax_score}"
    print(f"Expectimax differs from minimax ({expectimax_score:.2f} vs {minimax_score})")


def test_expectimax_searches_all_nodes():
    """Expectimax should search same nodes as minimax (no pruning possible)."""
    board = chess.Board()
    
    minimax = MiniMaxSearch(evaluate)
    expectimax = ExpectimaxSearch(evaluate)
    
    minimax.search(board, depth=3)
    expectimax.search(board, depth=3)
    
    assert expectimax.nodes_searched == minimax.nodes_searched, \
        f"Should search same nodes: {expectimax.nodes_searched} vs {minimax.nodes_searched}"
    print(f"Expectimax searches all nodes (no pruning): {expectimax.nodes_searched}")

def test_expectimax_more_optimistic():
    """Expectimax score should be optimistic (better than minimax's pessimistic assumption)."""
    board = chess.Board()
    
    minimax = MiniMaxSearch(evaluate)
    expectimax = ExpectimaxSearch(evaluate)
    
    _, minimax_score = minimax.search(board, depth=3)
    _, expectimax_score = expectimax.search(board, depth=3)
    
    # For white's turn: expectimax should be >= minimax (more optimistic)
    if board.turn == chess.WHITE:
        assert expectimax_score >= minimax_score, \
            f"Expectimax should be >= minimax for white: {expectimax_score} vs {minimax_score}"
    else:
        assert expectimax_score <= minimax_score, \
            f"Expectimax should be <= minimax for black: {expectimax_score} vs {minimax_score}"
    print("Expectimax score within expected bounds")

def run_all_tests():
    print("\n" + "="*50)
    print("Running Alpha Beta Search Tests")
    print("="*50 + "\n")
    
    test_finds_mate_in_one()
    test_alphabeta_equals_minimax()
    test_alphabeta_prunes()
    test_captures_hanging_piece()
    
    print("\n" + "="*50)
    print("Running Expectimax Tests")
    print("="*50 + "\n")

    test_expectimax_finds_forced_mate()
    test_expectimax_differs_from_minimax()
    test_expectimax_searches_all_nodes()
    test_expectimax_more_optimistic()

    print("\n" + "="*50)
    print("All search tests passed! ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()