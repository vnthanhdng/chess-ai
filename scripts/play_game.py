"""Interactive chess game using agent architecture."""

import sys
import time
import chess
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents import HumanAgent
from src.agents import AlphaBetaAgent
from src.evaluation import evaluate


def print_board(board: chess.Board) -> None:
    """
    Print the chess board in a readable format.
    
    Args:
        board: Current chess board state
    """
    print("\n" + "  a b c d e f g h")
    print("  " + "-" * 16)
    
    # Print from rank 8 to rank 1 (top to bottom)
    for rank in range(7, -1, -1):
        row = f"{rank + 1}|"
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece is None:
                row += ". "
            else:
                symbol = piece.symbol()
                row += f"{symbol} "
        print(row + f"|{rank + 1}")
    
    print("  " + "-" * 16)
    print("  a b c d e f g h\n")


def print_game_result(board: chess.Board, white_agent, black_agent) -> None:
    """
    Print the game result and statistics.
    
    Args:
        board: Final board state
        white_agent: White player agent
        black_agent: Black player agent
    """
    print("\n" + "=" * 50)
    print("GAME OVER")
    print("=" * 50)
    
    # Determine result
    if board.is_checkmate():
        winner = black_agent if board.turn == chess.WHITE else white_agent
        loser = white_agent if board.turn == chess.WHITE else black_agent
        print(f"Checkmate! {winner.name} wins!")
    elif board.is_stalemate():
        print("Stalemate - Draw")
    elif board.is_insufficient_material():
        print("Draw by insufficient material")
    elif board.is_fifty_moves():
        print("Draw by fifty-move rule")
    elif board.is_repetition():
        print("Draw by threefold repetition")
    else:
        print("Game drawn")
    
    # Print statistics
    print("\n" + "-" * 50)
    print("STATISTICS")
    print("-" * 50)
    
    for agent in [white_agent, black_agent]:
        stats = agent.get_stats()
        print(f"\n{agent}:")
        print(f"  Moves made:       {stats['moves_made']}")
        print(f"  Total time:       {stats['total_time']:.2f}s")
        
        if stats['moves_made'] > 0:
            print(f"  Avg time/move:    {stats['avg_time_per_move']:.2f}s")
        
        if stats['nodes_searched'] > 0:
            print(f"  Total nodes:      {stats['nodes_searched']:,}")
            print(f"  Avg nodes/move:   {stats['avg_nodes_per_move']:,.0f}")
    
    print("\n" + "=" * 50 + "\n")


def get_difficulty_settings() -> tuple[int, str]:
    """
    Prompt user for difficulty level.
    
    Returns:
        Tuple of (depth, difficulty_name)
    """
    print("\nChoose difficulty level:")
    print("  1. Easy   (depth 2)")
    print("  2. Medium (depth 3)")
    print("  3. Hard   (depth 4)")
    print("  4. Expert (depth 5)")
    
    difficulty_map = {
        '1': (2, 'Easy'),
        '2': (3, 'Medium'),
        '3': (4, 'Hard'),
        '4': (5, 'Expert')
    }
    
    while True:
        choice = input("> ").strip()
        if choice in difficulty_map:
            depth, name = difficulty_map[choice]
            return depth, name
        print("Invalid choice. Please enter 1, 2, 3, or 4.")


def play_game():
    """Main interactive game loop."""
    
    # Print welcome message
    print("\n" + "=" * 50)
    print("CHESS AI - Interactive Game")
    print("=" * 50)
    print("\nYou will play as White against the AI (Black).")
    print("Enter moves in UCI (e2e4) or SAN (Nf3, e4) format.")
    print("Type 'help' during the game for commands.\n")
    
    # Get difficulty settings
    ai_depth, difficulty_name = get_difficulty_settings()
    
    # Create agents
    human = HumanAgent(name="You", color=chess.WHITE)
    ai = AlphaBetaAgent(
        evaluator=evaluate,
        depth=ai_depth,
        name=f"AI ({difficulty_name})",
        color=chess.BLACK
    )
    
    print(f"\nStarting game: {human} vs {ai}")
    print("=" * 50)
    
    # Initialize board
    board = chess.Board()
    move_number = 1
    
    # Main game loop
    while not board.is_game_over():
        # Display board
        print_board(board)
        
        # Display evaluation
        score = evaluate(board)
        score_display = score / 100.0
        
        if score > 0:
            print(f"Position: +{score_display:.2f} (White advantage)")
        elif score < 0:
            print(f"Position: {score_display:.2f} (Black advantage)")
        else:
            print("Position: 0.00 (Equal)")
        print()
        
        # Determine whose turn it is
        current_agent = human if board.turn == chess.WHITE else ai
        
        # Get move
        if board.turn == chess.WHITE:
            # Human's turn
            print(f"Move {move_number}. {current_agent.name}'s turn (White)")
            move = current_agent.select_move(board)
            
            if move is None:
                print("\nGame ended by player.")
                return
            
            if move == "UNDO":
                continue
            
            move_str = board.san(move)
            board.push(move)
            print(f"→ {current_agent.name} played: {move_str}\n")
        
        else:
            # AI's turn
            print(f"Move {move_number}. {current_agent.name}'s turn (Black)")
            print("Thinking...", end=" ", flush=True)
            
            start_time = time.time()
            move = current_agent.select_move(board)
            elapsed = time.time() - start_time
            
            if move is None:
                print("\nAI resigns. You win!")
                break
            
            # Get search info
            search_info = current_agent.get_search_info()
            move_str = board.san(move)
            
            board.push(move)
            
            print(f"\r→ {current_agent.name} played: {move_str}")
            print(f"  (searched {search_info['nodes_searched']:,} nodes in {elapsed:.2f}s)")
            print()
            
            move_number += 1
    
    # Game over - display final position and results
    print_board(board)
    print_game_result(board, human, ai)


if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()