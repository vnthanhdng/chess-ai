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


def evaluate(board: chess.Board) -> int:
    """
    Evaluate board position.
    
    Returns:
        int: Score in centipawns (positive = white advantage)
    """
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    if board.is_checkmate():
        return -20000 if board.turn == chess.WHITE else 20000
    
    endgame = is_endgame(board)
    score = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        
        if piece is not None:
            material_value = PIECE_VALUES[piece.piece_type]
            positional_value = get_piece_square_value(piece, square, endgame=endgame)
            total_value = material_value + positional_value
            score += total_value if piece.color == chess.WHITE else -total_value

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