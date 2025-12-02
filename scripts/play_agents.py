#!/usr/bin/env python3
"""Run automated matches between two agents (agent vs agent)."""

import argparse
import chess
import time
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.base_agent import BaseAgent
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


def play_single_game(white_agent: BaseAgent, black_agent: BaseAgent, timeout_seconds: int = 120):
    board = chess.Board()

    start_game_time = time.time()

    while not board.is_game_over():
        # global timeout guard
        if time.time() - start_game_time > timeout_seconds:
            return "timeout", 0, 0

        current_agent = white_agent if board.turn == chess.WHITE else black_agent

        move = current_agent.select_move(board)
        if move is None:
            return "error", 0, 0

        board.push(move)

    # Determine outcome
    if board.is_checkmate():
        winner = "white" if board.turn == chess.BLACK else "black"
    else:
        winner = "draw"

    # compute average times
    white_avg = white_agent.total_time / white_agent.moves_made if white_agent.moves_made else 0
    black_avg = black_agent.total_time / black_agent.moves_made if black_agent.moves_made else 0

    return winner, white_avg, black_avg


def make_agents_play(white_agent: BaseAgent, black_agent: BaseAgent, iterations: int):
    results = {"white": 0, "black": 0, "draw": 0, "timeout": 0, "error": 0}
    w_times = []
    b_times = []

    for i in range(1, iterations + 1):
        print(f"\n=== Game {i}/{iterations} ===")
        # reset stats
        white_agent.reset_stats()
        black_agent.reset_stats()

        result, w_avg, b_avg = play_single_game(white_agent, black_agent)
        results[result] = results.get(result, 0) + 1
        w_times.append(w_avg)
        b_times.append(b_avg)

        print(f"Result: {result}")
        print(f"  White ({white_agent}): avg move time {w_avg:.4f}s")
        print(f"  Black ({black_agent}): avg move time {b_avg:.4f}s")

    print("\n=== Summary ===")
    print(results)
    if w_times:
        print(f"White mean move time: {sum(w_times)/len(w_times):.4f}s")
    if b_times:
        print(f"Black mean move time: {sum(b_times)/len(b_times):.4f}s")


def create_agent(agent_key: str, color: chess.Color, vi_iterations: int = 3):
    key = agent_key.lower()
    if key == "minimax":
        return MinimaxAgent(evaluate, depth=3, name="Minimax", color=color)
    if key == "alphabeta":
        return AlphaBetaAgent(evaluate, depth=3, name="AlphaBeta", color=color)
    if key == "expectimax":
        return ExpectimaxAgent(evaluate, depth=3, name="Expectimax", color=color)
    if key == "random":
        return RandomAgent(name="Random", color=color)
    if key == "simple":
        return SimpleAgent(name="Simple", color=color)
    if key == "qlearning":
        # set numTraining=0 to avoid long training during test runs
        return QLearningAgent(name="QLearning", color=color, numTraining=0, epsilon=0.0)
    if key == "valueiteration":
        return ValueIterationAgent(discount=0.9, iterations=vi_iterations, name="ValueIteration", color=color)

    raise RuntimeError(f"Unknown agent type '{agent_key}'")


def main():
    parser = argparse.ArgumentParser(description="Run automated agent vs agent matches")
    parser.add_argument("--white-agent", default="qlearning", help="Agent for White")
    parser.add_argument("--black-agent", default="valueiteration", help="Agent for Black")
    parser.add_argument("--num-games", type=int, default=1, help="Number of games to run")
    parser.add_argument("--vi-iterations", type=int, default=3, help="Iterations for ValueIterationAgent")
    args = parser.parse_args()

    white = create_agent(args.white_agent, chess.WHITE, vi_iterations=args.vi_iterations)
    black = create_agent(args.black_agent, chess.BLACK, vi_iterations=args.vi_iterations)

    print(f"Playing {args.num_games} games: White={white}, Black={black}")
    make_agents_play(white, black, iterations=args.num_games)


if __name__ == "__main__":
    main()
