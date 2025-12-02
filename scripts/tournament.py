"""
Round-robin tournament simulator for agents with Elo ratings.

This script runs matches between provided agent types, updates Elo
ratings after each game, and prints final standings.

Usage examples:
  python3 scripts/tournament.py --agents qlearning,valueiteration,random --games-per-pair 2
"""

import argparse
from pathlib import Path
import sys
import chess

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.agent_utils import create_agent, play_game

# Supported agent keys
SUPPORTED_AGENT_KEYS = [
    "minimax",
    "alphabeta",
    "expectimax",
    "random",
    "simple",
    "qlearning",
    "valueiteration",
]


def expected_score(rating_a: float, rating_b: float) -> float:
    """Return expected score for player A vs B."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def update_elo(r_a: float, r_b: float, score_a: float, k: float) -> tuple[float, float]:
    """Return updated ratings after a single game where A scored `score_a` (1/0.5/0)."""
    e_a = expected_score(r_a, r_b)
    e_b = expected_score(r_b, r_a)
    r_a_new = r_a + k * (score_a - e_a)
    r_b_new = r_b + k * ((1 - score_a) - e_b)
    return r_a_new, r_b_new


# use shared play_game from scripts.agent_utils


def run_tournament(agent_keys, games_per_pair=2, k=20, *, depth=2, q_numTraining=0, q_epsilon=0.0, vi_iterations=3, depths_map=None):
    # initialize ratings
    ratings = {k: 1200.0 for k in agent_keys}
    records = {k: {"wins": 0, "losses": 0, "draws": 0} for k in agent_keys}

    # play round-robin (including reversed colors)
    pairs = []
    for i in range(len(agent_keys)):
        for j in range(i + 1, len(agent_keys)):
            pairs.append((agent_keys[i], agent_keys[j]))

    for a, b in pairs:
        print(f"\n=== Match: {a} vs {b} ({games_per_pair} games) ===")
        for game_idx in range(games_per_pair):
            # alternate colors each game
            white_key, black_key = (a, b) if game_idx % 2 == 0 else (b, a)
            depth_w = depths_map.get(white_key, depth) if depths_map else depth
            depth_b = depths_map.get(black_key, depth) if depths_map else depth

            white = create_agent(white_key, chess.WHITE, depth=depth_w, vi_iterations=vi_iterations, q_numTraining=q_numTraining, q_epsilon=q_epsilon)
            black = create_agent(black_key, chess.BLACK, depth=depth_b, vi_iterations=vi_iterations, q_numTraining=q_numTraining, q_epsilon=q_epsilon)

            result = play_game(white, black)

            if result == "white":
                winner = white_key
                loser = black_key
                score_w = 1.0
            elif result == "black":
                winner = black_key
                loser = white_key
                score_w = 0.0
            elif result == "draw":
                winner = None
                loser = None
                score_w = 0.5
            else:
                print(f"Game ended with status: {result}. Treating as draw.")
                score_w = 0.5

            # Determine A and B in rating update (we update actual keys a,b)
            # We always update ratings with perspective of `a` vs `b`.
            if white_key == a:
                # A was white this game
                score_a = score_w
            else:
                # A was black
                # if score_w is 1 => white_key won which is b, so a lost => 0
                # score_a = 1 - score_w
                score_a = 1.0 - score_w

            r_a, r_b = ratings[a], ratings[b]
            r_a_new, r_b_new = update_elo(r_a, r_b, score_a, k)
            ratings[a], ratings[b] = r_a_new, r_b_new

            # update records
            if score_w == 1.0:
                # white won
                records[white_key]["wins"] += 1
                records[black_key]["losses"] += 1
            elif score_w == 0.0:
                records[black_key]["wins"] += 1
                records[white_key]["losses"] += 1
            else:
                records[a]["draws"] += 1
                records[b]["draws"] += 1

            print(f"Game {game_idx+1}: {white_key}(White) vs {black_key}(Black) -> {result}")
            print(f" Updated Elo: {a}: {ratings[a]:.1f}, {b}: {ratings[b]:.1f}")

    # final standings
    standings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    print("\n=== Final Standings (Elo) ===")
    for key, r in standings:
        rec = records[key]
        print(f"{key}: {r:.1f}  (W:{rec['wins']} L:{rec['losses']} D:{rec['draws']})")


def parse_args():
    parser = argparse.ArgumentParser(description="Run a round-robin tournament between agents")
    parser.add_argument("--agents", default="qlearning,valueiteration", help="Comma-separated agent keys")
    parser.add_argument("--games-per-pair", type=int, default=2, help="Number of games per pairing")
    parser.add_argument("--k", type=float, default=20.0, help="Elo K-factor per game")
    parser.add_argument("--depth", type=int, default=2, help="Search depth for search agents")
    parser.add_argument("--vi-iterations", type=int, default=3, help="Iterations for ValueIterationAgent")
    parser.add_argument("--q-train", type=int, default=0, help="Number of training episodes for QLearningAgent before matches")
    parser.add_argument("--q-epsilon", type=float, default=0.0, help="Exploration epsilon for QLearningAgent during matches")
    parser.add_argument("--depths", type=str, default=None, help="Optional comma-separated list of agent:depth to override default depth (e.g. minimax:3,alphabeta:2)")
    return parser.parse_args()


def main():
    args = parse_args()
    agent_keys = [s.strip().lower() for s in args.agents.split(",") if s.strip()]
    for k in agent_keys:
        if k not in SUPPORTED_AGENT_KEYS:
            raise RuntimeError(f"Unknown agent key: {k}. Available: {', '.join(SUPPORTED_AGENT_KEYS)}")

    # parse per-agent depths if provided
    depths_map = {}
    if args.depths:
        for pair in args.depths.split(','):
            if ':' in pair:
                key, val = pair.split(':', 1)
                key = key.strip().lower()
                try:
                    depths_map[key] = int(val)
                except ValueError:
                    raise RuntimeError(f"Invalid depth for {key}: {val}")

    run_tournament(
        agent_keys,
        games_per_pair=args.games_per_pair,
        k=args.k,
        depth=args.depth,
        q_numTraining=args.q_train,
        q_epsilon=args.q_epsilon,
        vi_iterations=args.vi_iterations,
        depths_map=depths_map,
    )


if __name__ == "__main__":
    main()
