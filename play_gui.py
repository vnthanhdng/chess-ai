"""Play chess with a GUI - human vs AI or watch two AIs play."""

import argparse
import chess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.gui import ChessGUI, play_game_with_gui, watch_agents_play
from src.agents import HumanAgent, MinimaxAgent, AlphaBetaAgent, ExpectimaxAgent
from evaluation import evaluate


def main():
    parser = argparse.ArgumentParser(description="Play chess with GUI")
    parser.add_argument(
        "--mode",
        choices=["human", "watch"],
        default="human",
        help="Game mode: 'human' to play against AI, 'watch' to watch two AIs play"
    )
    parser.add_argument(
        "--white-agent",
        choices=["human", "minimax", "alphabeta", "expectimax"],
        default="human",
        help="Agent for white (default: human)"
    )
    parser.add_argument(
        "--black-agent",
        choices=["human", "minimax", "alphabeta", "expectimax"],
        default="alphabeta",
        help="Agent for black (default: alphabeta)"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        choices=[2, 3, 4, 5],
        help="Search depth for AI agents (default: 3)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between moves in watch mode (seconds, default: 1.0)"
    )
    
    args = parser.parse_args()
    
    # Create agents (None means human player, handled by GUI)
    def create_agent(agent_type, color):
        if agent_type == "human":
            return None  # GUI handles human input
        elif agent_type == "minimax":
            return MinimaxAgent(evaluate, depth=args.depth, name="Minimax", color=color)
        elif agent_type == "alphabeta":
            return AlphaBetaAgent(evaluate, depth=args.depth, name="AlphaBeta", color=color)
        elif agent_type == "expectimax":
            return ExpectimaxAgent(evaluate, depth=args.depth, name="Expectimax", color=color)
        return None
    
    white_agent = create_agent(args.white_agent, chess.WHITE)
    black_agent = create_agent(args.black_agent, chess.BLACK)
    
    if args.mode == "watch":
        # Watch two agents play
        print(f"Watching {white_agent.name} (White) vs {black_agent.name} (Black)")
        print(f"Move delay: {args.delay} seconds")
        watch_agents_play(white_agent, black_agent, move_delay=args.delay)
    else:
        # Human vs AI
        white_name = white_agent.name if white_agent else "Human"
        black_name = black_agent.name if black_agent else "Human"
        print(f"Playing as {white_name} (White)")
        print(f"Against {black_name} (Black)")
        print("\nEnter moves in the text field (e.g., 'e2e4' or 'Nf3')")
        print("Or click on pieces and squares to make moves")
        play_game_with_gui(white_agent, black_agent)


if __name__ == "__main__":
    main()

