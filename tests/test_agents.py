"""Tests for agents."""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import chess
from src.agents import SearchAgent
from src.search import AlphaBetaSearch
from src.evaluation import evaluate


def test_agent_makes_legal_moves():
    """Agents should only make legal moves."""
    board = chess.Board()
    
    search = AlphaBetaSearch(evaluate)
    agent = SearchAgent(search, depth=2, name="TestAgent")
    
    move = agent.select_move(board)
    assert move in board.legal_moves, "Agent made illegal move"
    print("Agent makes legal moves")


def test_agent_handles_no_moves():
    """Agent should handle stalemate gracefully."""
    board = chess.Board(None)
    board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.A6, chess.Piece(chess.QUEEN, chess.WHITE))
    board.set_piece_at(chess.C7, chess.Piece(chess.KING, chess.WHITE))
    board.turn = chess.BLACK
    
    search = AlphaBetaSearch(evaluate)
    agent = SearchAgent(search, depth=2)
    
    move = agent.select_move(board)
    assert move is None, "Should return None when no legal moves"
    print("Agent handles no legal moves")


def run_all_tests():
    print("\n" + "="*50)
    print("Running Agent Tests")
    print("="*50 + "\n")
    
    test_agent_makes_legal_moves()
    test_agent_handles_no_moves()
    
    print("\n" + "="*50)
    print("All agent tests passed! ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()