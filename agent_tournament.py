"""
Lightweight agent-versus-agent runner using shared utilities.

This script used to duplicate play/timing logic; it now delegates to
`scripts.agent_utils` to keep behavior consistent with other scripts.
"""
import argparse
import chess
from scripts.agent_utils import create_agent, play_single_game_with_stats


def main():
    parser = argparse.ArgumentParser(description="Play games between two agents")
    parser.add_argument("--white-agent", default="minimax", help="Agent key for White")
    parser.add_argument("--black-agent", default="alphabeta", help="Agent key for Black")
    parser.add_argument("--depth", type=int, default=3, help="Default search depth for search agents")
    parser.add_argument("--num-games", type=int, default=1, help="Number of games to run")
    parser.add_argument("--vi-iterations", type=int, default=3, help="ValueIteration iterations")
    parser.add_argument("--q-train", type=int, default=0, help="QLearning training episodes")
    parser.add_argument("--q-epsilon", type=float, default=0.0, help="QLearning epsilon during matches")
    args = parser.parse_args()

    white = create_agent(args.white_agent, chess.WHITE, depth=args.depth, vi_iterations=args.vi_iterations, q_numTraining=args.q_train, q_epsilon=args.q_epsilon)
    black = create_agent(args.black_agent, chess.BLACK, depth=args.depth, vi_iterations=args.vi_iterations, q_numTraining=args.q_train, q_epsilon=args.q_epsilon)

    print(f"Running {args.num_games} games: White={white}, Black={black}")

    white_times = []
    black_times = []

    for i in range(1, args.num_games + 1):
        print(f"\n=== Game {i}/{args.num_games} ===")
        result = play_single_game_with_stats(white, black)
        print(f"Result: {result}")


    if white_times:
        print(f"\nWhite mean move time: {sum(white_times)/len(white_times):.4f}s")
    if black_times:
        print(f"Black mean move time: {sum(black_times)/len(black_times):.4f}s")


if __name__ == "__main__":
    main()
