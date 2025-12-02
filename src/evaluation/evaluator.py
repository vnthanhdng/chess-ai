"""Board evaluation functions."""

import chess
from .piece_square_tables import PIECE_SQUARE_TABLES, KING_ENDGAME_TABLE

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Bonuses and Penalties
PAWN_BONUS = {
    'doubled': -20,   # Penalty for two pawns on same file
    'isolated': -20,  # Penalty for no friendly pawns on adjacent files
    'passed': 50,     # Bonus for no enemy pawns ahead
    'shield': 15      # Bonus for pawns shielding the king
}

def is_endgame(board: chess.Board) -> bool:
    """Determine if the game is in endgame phase."""
    # Fast check: No queens usually means endgame
    w_queens = len(board.pieces(chess.QUEEN, chess.WHITE))
    b_queens = len(board.pieces(chess.QUEEN, chess.BLACK))
    
    if w_queens == 0 and b_queens == 0:
        return True
    
    # Check for "Queen + Pawns" or "Queen + 1 Minor" endings
    if w_queens == 1 and b_queens == 1:
        # Count material without queens/kings/pawns
        white_minors = len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.WHITE))
        black_minors = len(board.pieces(chess.KNIGHT, chess.BLACK)) + len(board.pieces(chess.BISHOP, chess.BLACK)) + len(board.pieces(chess.ROOK, chess.BLACK))
        if white_minors + black_minors <= 2:
            return True
            
    return False

def get_piece_square_value(piece: chess.Piece, square: chess.Square, endgame: bool = False) -> int:
    """Get piece-square table value."""
    piece_type = piece.piece_type
    
    # Mirror rank for Black (Tables are defined from White's perspective)
    if piece.color == chess.WHITE:
        rank = chess.square_rank(square)
        file = chess.square_file(square)
    else:
        rank = 7 - chess.square_rank(square)
        file = chess.square_file(square)
    
    if piece_type == chess.KING and endgame:
        table = KING_ENDGAME_TABLE
    else:
        table = PIECE_SQUARE_TABLES.get(piece_type)
        
    if table is None:
        return 0

    return table[rank][file]

def evaluate_pawns(board: chess.Board, color: chess.Color) -> int:
    """
    Evaluate pawn structure nuances: Doubled, Isolated, Passed.
    """
    score = 0
    pawns = board.pieces(chess.PAWN, color)
    opp_pawns = board.pieces(chess.PAWN, not color)
    
    # Convert bitboard to list of squares for easier iteration
    pawn_squares = list(pawns)
    
    files_with_pawns = [chess.square_file(sq) for sq in pawn_squares]
    
    for sq in pawn_squares:
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        
        # 1. Doubled Pawns (More than 1 pawn on this file)
        if files_with_pawns.count(file) > 1:
            score += PAWN_BONUS['doubled']
            
        # 2. Isolated Pawns (No friendly pawns on adjacent files)
        # Files are 0-7. Left is file-1, Right is file+1
        has_left_neighbor = (file - 1) in files_with_pawns
        has_right_neighbor = (file + 1) in files_with_pawns
        
        if not has_left_neighbor and not has_right_neighbor:
            score += PAWN_BONUS['isolated']
            
        # 3. Passed Pawns (No enemy pawns ahead on file or adjacent files)
        is_passed = True
        # Look at squares in front of us
        direction = 1 if color == chess.WHITE else -1
        check_rank = rank + direction
        
        while 0 <= check_rank <= 7:
            # Check file, left, and right on this rank for enemy pawns
            for f in range(max(0, file - 1), min(8, file + 2)):
                check_sq = chess.square(f, check_rank)
                if check_sq in opp_pawns:
                    is_passed = False
                    break
            if not is_passed:
                break
            check_rank += direction
            
        if is_passed:
            # Bonus increases as pawn advances
            advancement = rank if color == chess.WHITE else (7 - rank)
            score += PAWN_BONUS['passed'] + (advancement * 10)

    return score

def evaluate_king_safety(board: chess.Board, color: chess.Color) -> int:
    """
    Evaluate king safety based on pawn shield.
    Only relevant in Middle Game.
    """
    king_sq = board.king(color)
    if king_sq is None: return 0
    
    score = 0
    rank = chess.square_rank(king_sq)
    file = chess.square_file(king_sq)
    
    # If King is castled (on G or B file usually, or close to corner)
    if file > 4 or file < 3:
        # Check for pawns in front of the king
        pawns = board.pieces(chess.PAWN, color)
        direction = 1 if color == chess.WHITE else -1
        shield_rank = rank + direction
        
        if 0 <= shield_rank <= 7:
            # Check 3 files in front of king
            for f in range(max(0, file - 1), min(8, file + 2)):
                if chess.square(f, shield_rank) in pawns:
                    score += PAWN_BONUS['shield']
                elif chess.square(f, shield_rank + direction) in pawns:
                    # Pawn pushed one square is okay, but less safe
                    score += (PAWN_BONUS['shield'] // 2)
                    
    return score

def evaluate(board: chess.Board, ply_from_root: int = 0) -> int:
    """
    Comprehensive evaluation function.
    """
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    if board.is_checkmate():
        # Prefer faster mates
        return -20000 + ply_from_root if board.turn == chess.WHITE else 20000 - ply_from_root

    endgame = is_endgame(board)
    score = 0
    
    # 1. Material & Piece-Square Tables
    white_material = 0
    black_material = 0
    
    # piece_map() is faster than iterating all squares
    for square, piece in board.piece_map().items():
        material = PIECE_VALUES[piece.piece_type]
        pst = get_piece_square_value(piece, square, endgame)
        
        val = material + pst
        
        if piece.color == chess.WHITE:
            score += val
            white_material += material
        else:
            score -= val
            black_material += material

    # 2. Pawn Structure
    score += evaluate_pawns(board, chess.WHITE)
    score -= evaluate_pawns(board, chess.BLACK)
    
    # 3. King Safety
    if not endgame:
        score += evaluate_king_safety(board, chess.WHITE)
        score -= evaluate_king_safety(board, chess.BLACK)

    # 4. Endgame Mop-up
    if endgame:
        winning_side = None
        # Require significant material lead to attempt mop-up
        if white_material > black_material + 200:
            winning_side = chess.WHITE
        elif black_material > white_material + 200:
            winning_side = chess.BLACK

        if winning_side is not None:
            cmd_king = board.king(winning_side)
            losing_king = board.king(not winning_side)
            
            if cmd_king is not None and losing_king is not None:
                mop_up = 0
                
                # Push losing king to edge
                l_rank, l_file = chess.square_rank(losing_king), chess.square_file(losing_king)
                mop_up += (max(3 - l_rank, l_rank - 4) + max(3 - l_file, l_file - 4)) * 10
                
                # Bring winning king closer
                w_rank, w_file = chess.square_rank(cmd_king), chess.square_file(cmd_king)
                dist = abs(w_rank - l_rank) + abs(w_file - l_file)
                mop_up += (14 - dist) * 5
                
                score += mop_up if winning_side == chess.WHITE else -mop_up

    return score