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


def is_endgame(board: chess.Board) -> bool:
    """Determine if the game is in endgame phase."""
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    if queens == 0:
        return True
    
    if queens == 1:
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


def get_piece_square_value(piece: chess.Piece, square: chess.Square, endgame: bool = False) -> int:
    """Get piece-square table value."""
    piece_type = piece.piece_type
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    
    if piece.color == chess.BLACK:
        rank = 7 - rank
    
    if piece_type == chess.KING and endgame:
        table = KING_ENDGAME_TABLE
    else:
        table = PIECE_SQUARE_TABLES.get(piece_type)
        
    if table is None:
        return 0

    return table[rank][file]


def evaluate(board: chess.Board, ply_from_root: int = 0) -> int:
    """
    Improved evaluation with Draw fixes and End-game Mop-up.
    """
    if board.is_checkmate():
        # Prefer faster mates: Score is higher if ply is lower
        mate_score = 20000 - ply_from_root
        return -mate_score if board.turn == chess.WHITE else mate_score

    # Draws should be scored as 0 (Equality), not a massive penalty.
    # If the engine is losing, 0 is better than -1000.
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    # Standard material + positional evaluation
    endgame = is_endgame(board)
    score = 0
    
    # Calculate Material and PST
    white_material = 0
    black_material = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            material = PIECE_VALUES[piece.piece_type]
            pst = get_piece_square_value(piece, square, endgame=endgame)
            val = material + pst
            
            if piece.color == chess.WHITE:
                score += val
                white_material += material
            else:
                score -= val
                black_material += material

    winning_side = None
    if white_material > black_material + 200 and endgame:
        winning_side = chess.WHITE
    elif black_material > white_material + 200 and endgame:
        winning_side = chess.BLACK

    if winning_side is not None:
        mop_up_score = 0
        cmd_king = board.king(winning_side)
        losing_king = board.king(not winning_side)
        
        if cmd_king is not None and losing_king is not None:
            # 1. Force losing King to edge (Manhattan distance from center)
            # Center is 3.5, 3.5. 
            losing_rank, losing_file = chess.square_rank(losing_king), chess.square_file(losing_king)
            dist_from_center_rank = max(3 - losing_rank, losing_rank - 4)
            dist_from_center_file = max(3 - losing_file, losing_file - 4)
            mop_up_score += (dist_from_center_rank + dist_from_center_file) * 10
            
            # 2. Force winning King closer to losing King to help checkmate
            # Use simple Chebyshev distance calculation roughly
            rank_diff = abs(chess.square_rank(cmd_king) - losing_rank)
            file_diff = abs(chess.square_file(cmd_king) - losing_file)
            distance_between_kings = rank_diff + file_diff
            mop_up_score += (14 - distance_between_kings) * 5

            if winning_side == chess.WHITE:
                score += mop_up_score
            else:
                score -= mop_up_score

    # Return perspective-based score for Negamax, or absolute for Minimax
    # Assuming this function returns "White's Advantage":
    return score


def count_material(board: chess.Board) -> int:
    """Count material balance."""
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    return score