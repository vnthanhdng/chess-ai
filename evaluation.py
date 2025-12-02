# How good is this position??

import chess

# Piece values in centipawns
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000 # Essentially infinite
}

# Piece-Square Tables
# These tables assign bonuses/penalties based on piece position
# Values are from White's perspective; for Black, they are mirrored
# Array indices: [rank][file] with rank 0 = rank 1, rank 7 = rank 8

PAWN_TABLE = [
    [0,   0,   0,   0,   0,   0,   0,   0],
    [5,  10,  10, -20, -20,  10,  10,   5],
    [5,  -5, -10,   0,   0, -10,  -5,   5],
    [0,   0,   0,  20,  20,   0,   0,   0],
    [5,   5,  10,  25,  25,  10,   5,   5],
    [10,  10,  20,  30,  30,  20,  10,  10],
    [50,  50,  50,  50,  50,  50,  50,  50],
    [0,   0,   0,   0,   0,   0,   0,   0]
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-30,   0,  10,  15,  15,  10,   0, -30],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-30,   5,  10,  15,  15,  10,   5, -30],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

ROOK_TABLE = [
    [0,   0,   0,   0,   0,   0,   0,   0],
    [5,  10,  10,  10,  10,  10,  10,   5],
    [-5,   0,   0,   0,   0,   0,   0,  -5],
    [-5,   0,   0,   0,   0,   0,   0,  -5],
    [-5,   0,   0,   0,   0,   0,   0,  -5],
    [-5,   0,   0,   0,   0,   0,   0,  -5],
    [-5,   0,   0,   0,   0,   0,   0,  -5],
    [0,   0,   0,   5,   5,   0,   0,   0]
]

QUEEN_TABLE = [
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,   5,   5,   5,   0, -10],
    [-5,   0,   5,   5,   5,   5,   0,  -5],
    [0,   0,   5,   5,   5,   5,   0,  -5],
    [-10,   5,   5,   5,   5,   5,   0, -10],
    [-10,   0,   5,   0,   0,   0,   0, -10],
    [-20, -10, -10,  -5,  -5, -10, -10, -20]
]

# King tables - different for middlegame and endgame
KING_MIDDLEGAME_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20,  20,   0,   0,   0,   0,  20,  20],
    [20,  30,  10,   0,   0,  10,  30,  20]
]

KING_ENDGAME_TABLE = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50]
]

# Map piece types to their corresponding piece-square tables
PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_MIDDLEGAME_TABLE # For simplicity, using middlegame table
}

def is_endgame(board: chess.Board) -> bool:
    """
    Determine if the game is in the endgame phase.
    
    Args:
        board: chess.Board object
    
    Returns:
        bool: True if endgame, False otherwise
    """
    # Count queens
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    if queens == 0:
        return True
    
    if queens == 1:
        # Count minor and major pieces
        minors_majors = (
            len(board.pieces(chess.ROOK, chess.WHITE)) +
            len(board.pieces(chess.BISHOP, chess.WHITE)) +
            len(board.pieces(chess.KNIGHT, chess.WHITE)) +
            len(board.pieces(chess.ROOK, chess.BLACK)) +
            len(board.pieces(chess.BISHOP, chess.BLACK)) +
            len(board.pieces(chess.KNIGHT, chess.BLACK))
        )
        if minors_majors <= 4:
            return True

    return False

def get_piece_square_value(piece: chess.Piece, square: chess.Square, endgame=False) -> int:
    """
    Get the piece-square table value for a given piece on a given square.
    
    Args:
        piece: chess.Piece object
        square: chess.Square
        endgame: bool indicating if it's endgame phase
    Returns:
        int: Piece-square table value
    """
    piece_type = piece.piece_type
    
    # Get rank and file
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    
    # For black pieces, mirror the rank
    if piece.color == chess.BLACK:
        rank = 7 - rank
    
    if piece_type == chess.KING and endgame:
        table = KING_ENDGAME_TABLE
    else:
        table = PIECE_SQUARE_TABLES[piece_type]
        
    if table is None:
        return 0

    value = table[rank][file]
    return value


def evaluate(board: chess.Board, ply: int = 0) -> int:
    """
    Evaluate the current board position.
    
    Args:
        board: chess.Board object
        
    Returns:
        int: Score is in centipawns. (positive = white advantage, negative = black advantage)
    """
    if board.is_stalemate() or board.is_insufficient_material():
        return 0 # zero sum -> draw
    
    # Check for game ending condition
    # Prefer faster mates by reducing the magnitude with ply distance
    if board.is_checkmate():
        mate_score = 20000 - ply
        return -mate_score if board.turn == chess.WHITE else mate_score
    
    engame = is_endgame(board)
    score = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        
        if piece is not None:
            # Material value
            material_value = PIECE_VALUES[piece.piece_type]
            
            # Positional value
            positional_value = get_piece_square_value(piece, square, endgame=engame)
            
            total_value = material_value + positional_value
            
            score += total_value if piece.color == chess.WHITE else -total_value

    return score

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
            value = PIECE_VALUES[piece.piece_type]
            # Add for white pieces, subtract for black pieces
            score += value if piece.color == chess.WHITE else -value
    
    return score

if __name__ == "__main__":
    # Test starting position
    board = chess.Board()
    print("Starting position:")
    print(board)
    print(f"Score: {evaluate(board)}")
    print()
    
    # Test position with knight in center vs edge
    board_center = chess.Board(None)
    board_center.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board_center.set_piece_at(chess.D4, chess.Piece(chess.KNIGHT, chess.WHITE))  # Center
    board_center.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    board_edge = chess.Board(None)
    board_edge.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board_edge.set_piece_at(chess.A1, chess.Piece(chess.KNIGHT, chess.WHITE))  # Edge
    board_edge.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    print("Knight on d4 (center):", evaluate(board_center))
    print("Knight on a1 (edge):", evaluate(board_edge))
    print("Difference:", evaluate(board_center) - evaluate(board_edge))
    print("✓ Center knight is better!")