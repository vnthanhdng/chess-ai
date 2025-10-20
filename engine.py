import chess
from evaluation import evaluate

def find_best_move(board: chess.Board, depth: int) -> chess.Move:
    """
    Find the best move for the current player, given that they will look ahead 'depth' moves.
    
    Args:
        board: chess.Board object
        depth: int, depth of search (plies)
    
    Returns:
        chess.Move: The best move found, or None if no moves available.
    """
    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
    
    # Try all legal moves
    for move in board.legal_moves:
        board.push(move)
        move_value = minimax(board, depth - 1, board.turn == chess.WHITE)
        
        board.pop()
        
        # White's turn
        if board.turn == chess.WHITE:
            if move_value > best_value:
                best_value = move_value
                best_move = move
        else: # Black's turn
            if move_value < best_value:
                best_value = move_value
                best_move = move
    return best_move

def find_best_move_alpha_beta(board: chess.Board, depth: int) -> chess.Move:
    """
    Find the best move for the current player using the alpha-beta pruning algorithm.
    
    Args:
        board: chess.Board object
        depth: int, depth of search (plies)
    
    Returns:
        chess.Move: The best move found, or None if no moves available.
    """
    best_move = None
    best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
    alpha = float('-inf')
    beta = float('inf')

    for move in board.legal_moves:
        board.push(move)
        move_value = alpha_beta(board, depth - 1, alpha, beta, board.turn == chess.WHITE)
        board.pop()

        if board.turn == chess.WHITE:
            if move_value > best_value:
                best_value = move_value
                best_move = move
            alpha = max(alpha, move_value)
        else:
            if move_value < best_value:
                best_value = move_value
                best_move = move
            beta = min(beta, move_value)

    return best_move

def minimax(board: chess.Board, depth: int, maximizing: bool) -> int:
    """
    Minimax algorithm - recursively search the game tree.
    
    Args:
        board: chess.Board object
        depth: Remaining depth to search
        maximizing: True if maximizing, False if minimizing
    
    Returns:
        int: Evaluation score for this position
    """
    # Base case: reached max depth or game is over
    if depth == 0 or board.is_game_over():
        return evaluate(board)
    
    if maximizing:
        # White's turn - maximize the score
        max_eval = float('-inf')
        
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        # Black's turn - minimize the score
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval

def alpha_beta(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    """
    Alpha-beta pruning search. - optimized minimax that skips irrelevant branches
    
    Args:
        board: chess.Board object
        depth: int, depth of search (plies)
        alpha: int, best value maximizer can guarantee, initially -inf
        beta: int, best value minimizer can guarantee, initially inf
        maximizing: bool, True if maximizing player, False if minimizing player

    Returns:
        int: The evaluation score for the position
    """
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval = alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


if __name__ == "__main__":
    import time
    
    # Create a position
    board = chess.Board()
    print("Starting position:")
    print(board)
    print()
    
    # Test basic minimax
    print("Finding best move with minimax (depth 3)...")
    start_time = time.time()
    best_move = find_best_move(board, depth=3)
    elapsed = time.time() - start_time
    print(f"Best move: {best_move}")
    print(f"Time: {elapsed:.2f} seconds")
    print()
    
    # Test alpha-beta
    print("Finding best move with alpha-beta (depth 3)...")
    start_time = time.time()
    best_move_ab = find_best_move_alpha_beta(board, depth=3)
    elapsed_ab = time.time() - start_time
    print(f"Best move: {best_move_ab}")
    print(f"Time: {elapsed_ab:.2f} seconds")
    print(f"Speedup: {elapsed/elapsed_ab:.1f}x faster!")
    print()
    
    # Make the move and show the result
    board.push(best_move_ab)
    print("After AI move:")
    print(board)