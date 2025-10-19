# Game loop

import chess
import chess.svg
from engine import find_best_move_alpha_beta
from evaluation import evaluate

def print_board(board: chess.Board):
    """ Print the chess board in a readable format. """
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
                # white pieces uppercase, black pieces lowercase
                row += f" {symbol}"
        print(row + f"|{rank + 1}")
    print("  " + "-" * 16)
    print("  a b c d e f g h\n")
    
def get_human_move(board: chess.Board) -> chess.Move:
    """
    Get a move from the human player.
    
    Args:
        board: chess.Board object
        
    Returns:
        chess.Move: the move entered by the human
    """
    while True:
        print("Enter your move (e.g., e2e4 or e4 for pawn move)")
        print("Type 'moves' for legal moves, 'quit' to exit, 'help' for commands.")
        
        user_input = input("> ").strip().lower()
        
        if user_input == 'quit':
            print("Thanks for playing!")
            return None
        
        if user_input == 'help':
            print("\nCommands:")
            print("  - Enter moves in UCI format (e.g., 'e2e4')")
            print("  - Or algebraic notation (e.g., 'Nf3', 'e4')")
            print("  - 'moves' - show all legal moves")
            print("  - 'quit' - exit the game")
            print("  - 'undo' - take back your last move")
            print()
            continue
        
        if user_input == 'moves':
            print("\nLegal moves:")
            moves_list = [board.san(move) for move in board.legal_moves]
            # print in columns
            for i in range(0, len(moves_list), 6):
                print("  " + ", ".join(moves_list[i:i+6]))
            print()
            continue
        
        # this is so cheating.
        if user_input == 'undo':
            if len(board.move_stack) >= 2:
                board.pop() # undo AI move
                board.pop() # undo human move
                print("Moves undone.")
                return "UNDO"
            else:
                print("No moves to undo.")
                continue
            
        try:
            # Try UCI format first
            if len(user_input) in [4, 5] and user_input[0] in 'abcdefgh' and user_input[2] in 'abcdefgh': # e2e4 or e7e8q
                move = chess.Move.from_uci(user_input)
            else:
                # Try SAN format
                move = board.parse_san(user_input)
            
            # check if move is legal
            if move in board.legal_moves:
                return move
            else:
                print("Illegal move. Try again.")
        except (ValueError, chess.InvalidMoveError, chess.AmbiguousMoveError, chess.IllegalMoveError):
            print("Invalid move format. Try again.")
            print("Example: e2e4 or Nf3")
            
def play_game():
    """ Main game loop. """
    board = chess.Board()
    
    print("=" * 50)
    print("Welcome to Chess AI!")
    print("=" * 50)
    print("You are playing as White. Enter moves in UCI (e2e4) or SAN (e4, Nf3) format.")
    print("Type 'help' for commands.")
    
    ai_depth = 3
    
    print("Choose difficulty level:")
    print("1. Easy (depth 2)")
    print("2. Medium (depth 3)")
    print("3. Hard (depth 4)")
    print("4. Expert (depth 5)")
    
    while True:
        difficulty = input("> ").strip()
        if difficulty in ['1', '2', '3', '4']:
            ai_depth = int(difficulty) + 1
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    print()
    
    move_number = 1
    while not board.is_game_over():
        print_board(board)
        
        score = evaluate(board)
        score_display = score / 100.0
        
        if score > 0:
            print(f"Position score: +{score_display:.2f} (White advantage)")
        elif score < 0:
            print(f"Position score: {score_display:.2f} (Black advantage)")
        else:
            print("Position score: 0.00 (Equal)")
        print()
        
        if board.turn == chess.WHITE:
            print(f"Move {move_number}. Your turn (White).")
            human_move = get_human_move(board)
            if human_move is None:
                return # quit game
            if human_move == "UNDO":
                print_board(board)
                continue
            move_san = board.san(human_move)
            board.push(human_move)
            print(f"You played: {move_san}")
        else:
            print(f"Move {move_number}. AI's turn (Black). Thinking...")
            import time
            start_time = time.time()
            ai_move = find_best_move_alpha_beta(board, ai_depth)
            elapsed = time.time() - start_time
            
            if ai_move is None:
                print("AI resigns. You win!")
                break
            move_san = board.san(ai_move)
            board.push(ai_move)
            print(f"AI played: {move_san}")
            move_number += 1
    
    print_board(board)
    print("=" * 50)
    print("Game over!")
    print("=" * 50)
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            print("Checkmate! Black (AI) wins!")
        else:
            print("Checkmate! You win!")
    elif board.is_stalemate():
        print("Stalemate! It's a draw.")
    elif board.is_insufficient_material():
        print("Draw by insufficient material.")
    elif board.is_fifty_moves():
        print("Draw by fifty-move rule.")
    elif board.is_repetition():
        print("Draw by threefold repetition.")
    else:
        print("Game drawn.")
    
    print()


if __name__ == "__main__":
    play_game()