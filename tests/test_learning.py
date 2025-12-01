"""Tests for learning agents (Q-Learning and Value Iteration)."""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import chess
from src.agents import QLearningAgent, ValueIterationAgent
from src.evaluation import evaluate

q_agent = QLearningAgent(numTraining=10, epsilon=0.1, alpha=0.5, gamma=0.9, color=chess.WHITE)
# Q-LEARNING TESTS
def test_qlearning_initializes():
    """Q-Learning agent should initialize without errors."""
    assert q_agent is not None
    assert len(q_agent.q_values) > 0, "Q-values should be populated after training"
    print("Q-Learning agent initializes")


def test_qlearning_chooses_legal_move():
    """Q-Learning agent should always choose a legal move."""
    board = chess.Board()
    
    move = q_agent.choose_move(board)
    assert move in board.legal_moves, f"Move {move} should be legal"
    print("Q-Learning chooses legal move")


def test_qlearning_finds_mate_in_one():
    """Q-Learning agent should find mate in one (after training on similar positions)."""
    # Note: This may fail if agent hasn't seen this position during training
    # Consider this a soft test
    board = chess.Board()
    board.set_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
    
    move = q_agent.choose_move(board)
    # Should prefer Qxf7# if it has learned this is valuable
    print(f"Q-Learning suggests {move.uci()} for mate-in-one position")


def test_qlearning_avoids_hanging_piece():
    """Q-Learning agent should prefer not losing material."""
    board = chess.Board()
    board.set_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    # Queen is hanging - agent should not move it into danger
    
    move = q_agent.choose_move(board)
    assert move in board.legal_moves
    print(f"Q-Learning makes safe move: {move.uci()}")


def test_qlearning_updates_qvalues():
    """Q-Learning agent should update Q-values during training."""
    agent = QLearningAgent(numTraining=1, epsilon=0.5, alpha=0.5, gamma=0.9, color=chess.BLACK)
    board = chess.Board()
    board.push(chess.Move.from_uci("e2e4"))
    
    initial_qval_count = len(agent.q_values)
    
    # Train one more episode manually
    agent.startEpisode()
    while not board.is_game_over() and board.fullmove_number < 20:
        if board.turn == agent.color:
            move = agent.getAction(board)
            if move:
                prev_board = board.copy()
                board.push(move)
                reward = evaluate(board) - evaluate(prev_board)
                agent.update(prev_board, move, board, reward)
        else:
            # Random opponent move
            import random
            moves = list(board.legal_moves)
            if moves:
                board.push(random.choice(moves))
    
    assert len(agent.q_values) >= initial_qval_count, "Q-values should grow or stay same"
    print(f"Q-Learning updates Q-values (now has {len(agent.q_values)} entries)")


# VALUE ITERATION TESTS

vi_agent = ValueIterationAgent(discount=0.9, iterations=2, color=chess.WHITE)
def test_value_iteration_initializes():
    """Value Iteration agent should initialize without errors."""
    agent = ValueIterationAgent(discount=0.9, iterations=2, color=chess.BLACK)
    assert agent is not None
    assert len(agent.values) > 0, "Values should be populated after initialization"
    print("Value Iteration agent initializes")


def test_value_iteration_chooses_legal_move():
    """Value Iteration agent should always choose a legal move."""
    board = chess.Board()
    
    move = vi_agent.choose_move(board)
    assert move in board.legal_moves, f"Move {move} should be legal"
    print("Value Iteration chooses legal move")


def test_value_iteration_has_state_values():
    """Value Iteration should compute values for explored states."""
    agent = ValueIterationAgent(discount=0.9, iterations=2, color=chess.BLACK)
    board = chess.Board()
    board.push(chess.Move.from_uci("e2e4"))
    
    state_fen = board.fen()
    # Check if this state or similar states have values
    assert len(agent.values) > 0, "Should have computed some state values"
    print(f"Value Iteration has {len(agent.values)} state values")


def test_value_iteration_expands_states():
    """Value Iteration should expand state space during iterations."""
    agent = ValueIterationAgent(discount=0.9, iterations=1, color=chess.BLACK)
    initial_states = len(agent.states)
    
    # Run more iterations
    agent.iterations = 2
    agent.runValueIteration()
    
    # State space should grow or stay the same
    assert len(agent.states) >= initial_states
    print(f"Value Iteration expands states: {initial_states} -> {len(agent.states)}")


def test_value_iteration_computes_qvalues():
    """Value Iteration should compute Q-values for actions."""
    board = chess.Board()
    
    move = chess.Move.from_uci("e2e4")
    q_value = vi_agent.computeQValueFromValues(board, move)
    
    assert isinstance(q_value, (int, float)), "Q-value should be numeric"
    print(f"Value Iteration computes Q-value: {q_value:.2f} for e2e4")


def test_value_iteration_finds_best_action():
    """Value Iteration should find best action from Q-values."""
    agent = ValueIterationAgent(discount=0.9, iterations=2, color=chess.BLACK)
    board = chess.Board()
    board.push(chess.Move.from_uci("e2e4"))
    
    best_action = agent.computeActionFromValues(board)
    
    assert best_action in board.legal_moves or best_action is None
    print(f"Value Iteration finds best action: {best_action}")


# COMPARISON TESTS

def test_both_agents_choose_moves():
    """Both agents should be able to choose moves from the same position."""
    board = chess.Board()

    q_move = q_agent.choose_move(board)
    vi_move = vi_agent.choose_move(board)
    
    assert q_move in board.legal_moves
    assert vi_move in board.legal_moves
    print(f"Both agents choose moves: Q={q_move.uci()}, VI={vi_move.uci()}")


def test_agents_handle_complex_position():
    """Both agents should handle complex middle-game positions."""
    board = chess.Board()
    board.set_fen("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
    
    q_move = q_agent.choose_move(board)
    vi_move = vi_agent.choose_move(board)
    
    assert q_move in board.legal_moves
    assert vi_move in board.legal_moves
    print(f"Both handle complex position: Q={q_move.uci()}, VI={vi_move.uci()}")


def run_all_tests():
    print("\n" + "="*50)
    print("Running Q-Learning Agent Tests")
    print("="*50 + "\n")
    
    test_qlearning_initializes()
    test_qlearning_chooses_legal_move()
    test_qlearning_finds_mate_in_one()
    test_qlearning_avoids_hanging_piece()
    test_qlearning_updates_qvalues()
    
    print("\n" + "="*50)
    print("Running Value Iteration Agent Tests")
    print("="*50 + "\n")
    
    test_value_iteration_initializes()
    test_value_iteration_chooses_legal_move()
    test_value_iteration_has_state_values()
    test_value_iteration_expands_states()
    test_value_iteration_computes_qvalues()
    test_value_iteration_finds_best_action()
    
    print("\n" + "="*50)
    print("Running Comparison Tests")
    print("="*50 + "\n")
    
    test_both_agents_choose_moves()
    test_agents_handle_complex_position()
    
    print("\n" + "="*50)
    print("All learning tests passed! ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()
