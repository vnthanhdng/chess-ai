"""
Utilities for creating agents and running games.

Centralizes agent factory logic so scripts can reuse the same constructors
and parameters (depth, training iterations, etc.).
"""
from typing import Callable
from pathlib import Path
import sys
import chess
import time

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents import (
    MinimaxAgent,
    AlphaBetaAgent,
    ExpectimaxAgent,
    RandomAgent,
    SimpleAgent,
    QLearningAgent,
    ValueIterationAgent,
)
from src.evaluation import evaluate


def create_agent(agent_key: str, color: chess.Color, *, depth: int = 3, vi_iterations: int = 3, q_numTraining: int = 0, q_epsilon: float = 0.0):
    """Create an agent instance from a short key.

    Parameters are provided with sane defaults for fast tests.
    """
    key = agent_key.lower()
    if key == "minimax":
        return MinimaxAgent(evaluate, depth=depth, name="Minimax", color=color)
    if key == "alphabeta":
        return AlphaBetaAgent(evaluate, depth=depth, name="AlphaBeta", color=color)
    if key == "expectimax":
        return ExpectimaxAgent(evaluate, depth=depth, name="Expectimax", color=color)
    if key == "random":
        return RandomAgent(name="Random", color=color)
    if key == "simple":
        return SimpleAgent(name="Simple", color=color)
    if key == "qlearning":
        return QLearningAgent(name="QLearning", color=color, numTraining=q_numTraining, epsilon=q_epsilon)
    if key == "valueiteration":
        return ValueIterationAgent(discount=0.9, iterations=vi_iterations, name="ValueIteration", color=color)

    raise RuntimeError(f"Unknown agent type '{agent_key}'")


def play_game(white_agent, black_agent, timeout_seconds: int = 120):
    """Play one game between two agents. Returns outcome string: 'white','black','draw','timeout','error'."""
    board = chess.Board()
    start_time = time.time()
    white_agent.startEpisode()
    black_agent.startEpisode()
    while not board.is_game_over():
        if time.time() - start_time > timeout_seconds:
            return "timeout"

        current = white_agent if board.turn == chess.WHITE else black_agent
        move = current.select_move(board)
        if move is None:
            return "error"
        board.push(move)
    
    white_agent.stopEpisode()
    black_agent.stopEpisode()

    if board.is_checkmate():
        return "white" if board.turn == chess.BLACK else "black"
    return "draw"


def play_single_game_with_stats(white_agent, black_agent, timeout_seconds: int = 120):
    """Play a game and return (result, white_avg_time, black_avg_time)."""
    result = play_game(white_agent, black_agent, timeout_seconds)
    white_avg = white_agent.total_time / white_agent.moves_made if white_agent.moves_made else 0
    black_avg = black_agent.total_time / black_agent.moves_made if black_agent.moves_made else 0
    return result, white_avg, black_avg
