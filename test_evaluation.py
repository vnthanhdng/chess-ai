import chess
from evaluation import evaluate

def test_starting_position():
    """Starting position should be equal (score = 0)"""
    board = chess.Board()
    score = evaluate(board)
    assert score == 0, f"Starting position should be 0, got {score}"
    print("Starting position test passed")

def test_white_up_pawn():
    """White up a pawn should be +100"""
    board = chess.Board()
    board.remove_piece_at(chess.E7)
    score = evaluate(board)
    assert score == 100, f"White up a pawn should be +100, got {score}"
    print("White up a pawn passed")
    
def test_black_up_queen():
    """Black up a queen should be -900"""
    board = chess.Board()
    board.remove_piece_at(chess.D1)
    score = evaluate(board)
    assert score == -900, f"Black up a queen should be -900, got {score}"
    print("Black up a queen test passed")
    
def test_complex_position():
    """Test a complex position with known material balance"""
    # Position: White has R+B vs Black's N+N (Rook+Bishop vs two Knights)
    # White: King on e1, Rook on a1, Bishop on c1
    # Black: King on e8, Knight on b8, Knight on g8
    board = chess.Board(None)  # Empty board
    
    # White pieces
    board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.A1, chess.Piece(chess.ROOK, chess.WHITE))
    board.set_piece_at(chess.C1, chess.Piece(chess.BISHOP, chess.WHITE))
    
    # Black pieces
    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.B8, chess.Piece(chess.KNIGHT, chess.BLACK))
    board.set_piece_at(chess.G8, chess.Piece(chess.KNIGHT, chess.BLACK))
    
    score = evaluate(board)
    # White: 20000 + 500 + 330 = 20830
    # Black: 20000 + 320 + 320 = 20640
    # Difference: +190
    expected = 190
    assert score == expected, f"Expected {expected}, got {score}"
    print("Complex position test passed")
    
def test_checkmate_white_wins():
    """Checkmate should return winning score for White"""
    # Scholar's mate position
    board = chess.Board()
    moves = ["e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6", "Qxf7#"]
    for move in moves:
        board.push_san(move)
    
    score = evaluate(board)
    assert score == 20000, f"White checkmate should be +20000, got {score}"
    print("Checkmate (White wins) test passed")


def test_checkmate_black_wins():
    """Checkmate should return losing score for White"""
    # Fool's mate - fastest checkmate
    board = chess.Board()
    moves = ["f3", "e5", "g4", "Qh4#"]
    for move in moves:
        board.push_san(move)
    
    score = evaluate(board)
    assert score == -20000, f"Black checkmate should be -20000, got {score}"
    print("Checkmate (Black wins) test passed")


def test_stalemate():
    """Stalemate should return 0 (draw)"""
    # Create a stalemate position
    board = chess.Board(None)
    board.set_piece_at(chess.H8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.F7, chess.Piece(chess.QUEEN, chess.WHITE))
    board.set_piece_at(chess.F6, chess.Piece(chess.KING, chess.WHITE))
    board.turn = chess.BLACK  # Black to move - stalemate
    
    assert board.is_stalemate(), "Board set up should be a stalemate"
    
    score = evaluate(board)
    assert score == 0, f"Stalemate should be 0, got {score}"
    print("Stalemate test passed")


def test_material_count_symmetry():
    """Material count should be symmetric (White's perspective vs Black's)"""
    board = chess.Board()
    
    # Remove same piece from both sides
    board.remove_piece_at(chess.B1)  # White knight
    board.remove_piece_at(chess.B8)  # Black knight
    
    score = evaluate(board)
    assert score == 0, f"Symmetric position should be 0, got {score}"
    print("Material symmetry test passed")
    
def test_insufficient_material():
    """Insufficient material should be a draw (score = 0)"""
    # King vs King
    board = chess.Board(None)
    board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    score = evaluate(board)
    assert score == 0, f"Insufficient material should be 0, got {score}"
    print("Insufficient material test passed")
    
def run_all_tests():
    """Run all test functions"""
    print("\n" + "="*50)
    print("Running Evaluation Tests")
    print("="*50 + "\n")
    
    test_starting_position()
    test_white_up_pawn()
    test_black_up_queen()
    test_complex_position()
    test_checkmate_white_wins()
    test_checkmate_black_wins()
    test_stalemate()
    test_material_count_symmetry()
    test_insufficient_material()
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()