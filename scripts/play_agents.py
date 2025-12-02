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
from scripts.agent_utils import create_agent, play_game as play_game_simple
from src.evaluation import evaluate


def play_single_game(white_agent: BaseAgent, black_agent: BaseAgent, timeout_seconds: int = 120):
    return play_game_simple(white_agent, black_agent, timeout_seconds)


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


def create_agent_from_key(agent_key: str, color: chess.Color, *, depth: int = 3, vi_iterations: int = 3, q_numTraining: int = 0, q_epsilon: float = 0.0):
    # thin wrapper to preserve CLI API used previously; forwards parameters to shared factory
    return create_agent(agent_key, color, depth=depth, vi_iterations=vi_iterations, q_numTraining=q_numTraining, q_epsilon=q_epsilon)


def main():
    parser = argparse.ArgumentParser(description="Run automated agent vs agent matches")
    parser.add_argument("--white-agent", default="qlearning", help="Agent for White")
    parser.add_argument("--black-agent", default="valueiteration", help="Agent for Black")
    parser.add_argument("--num-games", type=int, default=1, help="Number of games to run")
    parser.add_argument("--depth", type=int, default=3, help="Default search depth for search agents")
    parser.add_argument("--white-depth", type=int, default=None, help="Search depth for White agent (overrides --depth)")
    parser.add_argument("--black-depth", type=int, default=None, help="Search depth for Black agent (overrides --depth)")
    parser.add_argument("--vi-iterations", type=int, default=3, help="Iterations for ValueIterationAgent")
    parser.add_argument("--q-train", type=int, default=0, help="Number of training episodes for QLearningAgent before matches")
    parser.add_argument("--q-epsilon", type=float, default=0.0, help="Exploration epsilon for QLearningAgent during matches")
    args = parser.parse_args()

    depth_white = args.white_depth if args.white_depth is not None else args.depth
    depth_black = args.black_depth if args.black_depth is not None else args.depth

    white = create_agent_from_key(args.white_agent, chess.WHITE, depth=depth_white, vi_iterations=args.vi_iterations, q_numTraining=args.q_train, q_epsilon=args.q_epsilon)
    black = create_agent_from_key(args.black_agent, chess.BLACK, depth=depth_black, vi_iterations=args.vi_iterations, q_numTraining=args.q_train, q_epsilon=args.q_epsilon)

    print(f"Playing {args.num_games} games: White={white}, Black={black}")
    make_agents_play(white, black, iterations=args.num_games)


if __name__ == "__main__":
    main()
