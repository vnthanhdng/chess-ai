import argparse
import chess
import time
from src.agents.base_agent import BaseAgent
from src.agents import MinimaxAgent, AlphaBetaAgent, ExpectimaxAgent
from evaluation import evaluate


def play_single_game(white_agent: BaseAgent, black_agent: BaseAgent, timeout_seconds: int = 120):
    """
    Play one game between agents with a hard timeout and move-time tracking.
    Returns:
        result (str): "white", "black", "draw", or "timeout"
        white_avg (float)
        black_avg (float)
    """
    board = chess.Board()

    white_times = []
    black_times = []

    start_game_time = time.time()

    while not board.is_game_over():
        # Hard 2 minute timeout
        if time.time() - start_game_time > timeout_seconds:
            print("Game terminated due to timeout.")
            return "timeout", 0, 0

        current_agent = white_agent if board.turn == chess.WHITE else black_agent

        move_start = time.time()
        print(f"{current_agent}")
        move = current_agent.choose_move(board)
        move_end = time.time()

        if move is None:
            print("Error: Agent returned None move.")
            return "error", 0, 0

        # Track move time
        if board.turn == chess.WHITE:
            white_times.append(move_end - move_start)
        else:
            black_times.append(move_end - move_start)

        board.push(move)

    # Compute averages
    white_avg = sum(white_times) / len(white_times) if white_times else 0
    black_avg = sum(black_times) / len(black_times) if black_times else 0

    # Determine outcome
    if board.is_checkmate():
        winner = "white" if board.turn == chess.BLACK else "black"
    else:
        winner = "draw"

    return winner, white_avg, black_avg


def make_agents_play(white_agent: BaseAgent, black_agent: BaseAgent, iterations: int):
    """
    Run `iterations` number of games and report average move times.
    """
    white_avg_list = []
    black_avg_list = []

    for game_idx in range(1, iterations + 1):
        print(f"\n=== Starting Game {game_idx}/{iterations} ===")
        result, w_avg, b_avg = play_single_game(white_agent, black_agent)

        print(f"Game {game_idx} result: {result}")
        print(f"  White ({white_agent.name}) avg move time: {w_avg:.4f} sec")
        print(f"  Black({black_agent.name}) avg move time: {b_avg:.4f} sec")

        white_avg_list.append(w_avg)
        black_avg_list.append(b_avg)

    print("\n===== FINAL RESULTS ACROSS ALL GAMES =====")
    print(f"{white_agent.name} mean move time: {sum(white_avg_list)/iterations:.4f} sec")
    print(f"{black_agent.name} mean move time: {sum(black_avg_list)/iterations:.4f} sec")


def main():
    parser = argparse.ArgumentParser(description="Play chess with agents")
    parser.add_argument(
        "--white-agent",
        choices=["minimax", "alphabeta", "expectimax"],
        default="minimax",
    )
    parser.add_argument(
        "--black-agent",
        choices=["minimax", "alphabeta", "expectimax"],
        default="alphabeta",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        choices=[2, 3, 4, 5],
        help="Search depth for AI agents (default: 3)",
    )
    parser.add_argument(
        "--num-games",
        type=int,
        default=1,
        help="Number of games to run (default: 1)"
    )
    args = parser.parse_args()

    def create_agent(agent_type, color):
        if agent_type == "minimax":
            return MinimaxAgent(evaluate, depth=args.depth, name="Minimax", color=color)
        elif agent_type == "alphabeta":
            return AlphaBetaAgent(evaluate, depth=args.depth, name="AlphaBeta", color=color)
        elif agent_type == "expectimax":
            return ExpectimaxAgent(evaluate, depth=args.depth, name="Expectimax", color=color)
        raise RuntimeError("Invalid agent type")

    white_agent = create_agent(args.white_agent, chess.WHITE)
    black_agent = create_agent(args.black_agent, chess.BLACK)

    print(f"Running {args.num_games} games:")
    print(f"  White = {white_agent.name}")
    print(f"  Black = {black_agent.name}")

    make_agents_play(white_agent, black_agent, iterations=args.num_games)


if __name__ == "__main__":
    main()
