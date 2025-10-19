# How good is this position??

import chess

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000 # Essentially infinite
}

def evaluate(board: chess.Board) -> int:
    """
    Evaluate the current board position.
    
    Args:
        board: chess.Board object
        
    Returns:
        int: Score is in centipawns. (positive = white advantage, negative = black advantage)
    """
    # Check for game ending condition
    if board.is_checkmate():
        return -20000 if board.turn == chess.WHITE else 20000
    
    if board.is_stalemate() or board.is_insufficient_material():
        return 0 # zero sum -> draw
    
    return count_material(board)

def count_material(board: chess.Board) -> int:
    """
    Count material balance on the board.
    
    Args:
        board: chess.Board object
        
    Returns:
        int: Material balance in centipawns.
    """
    score = 0
    
    # Iterate through all squares on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        
        if piece is not None:
            # Get the value
            value = piece_values[piece.piece_type]
            # Add for white pieces, subtract for black pieces
            score += value if piece.color == chess.WHITE else -value
    
    return score

if __name__ == "__main__":
    board = chess.Board()
    print(board)
    print(f"Starting position score: {evaluate(board)}")
    
    # Quick sanity check
    assert evaluate(board) == 0, "Starting position should be equal"
    print("Basic sanity check passed")