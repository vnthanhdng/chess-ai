import chess
import pathlib
import sys
project_root = pathlib.Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from src.evaluation import evaluate, is_endgame, get_piece_square_value, evaluate_pawns, evaluate_king_safety


def test_starting_position():
    """Starting position should be approximately equal (close to 0)"""
    board = chess.Board()
    score = evaluate(board)
    # With piece-square tables, starting position won't be exactly 0
    # but should be very close (within 50 centipawns)
    assert abs(score) < 50, f"Starting position should be close to 0, got {score}"
    print("Starting position test passed")


def test_material_difference():
    """Material differences should still dominate evaluation"""
    board = chess.Board()
    board.remove_piece_at(chess.E7)  # Remove black pawn
    score = evaluate(board)
    # Should be positive (White ahead) and roughly around 100 (pawn value)
    assert score > 50, f"White up a pawn should be positive, got {score}"
    assert score < 150, f"White up a pawn should be around 100, got {score}"
    print("Material difference test passed")


def test_black_up_queen():
    """Black up a queen should be significantly negative"""
    board = chess.Board()
    board.remove_piece_at(chess.D1)  # Remove white queen
    score = evaluate(board)
    # Should be very negative (around -900 for queen)
    assert score < -850, f"Black up a queen should be around -900, got {score}"
    assert score > -950, f"Black up a queen should be around -900, got {score}"
    print("Black up queen test passed")


def test_knight_center_vs_edge():
    """Knight in center should be better than knight on edge"""
    # Knight on d4 (center)
    board_center = chess.Board(None)
    board_center.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board_center.set_piece_at(chess.D4, chess.Piece(chess.KNIGHT, chess.WHITE))
    board_center.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    # Add pawns to prevent is_insufficient_material()
    board_center.set_piece_at(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
    board_center.set_piece_at(chess.A7, chess.Piece(chess.PAWN, chess.BLACK))

    
    # Knight on a1 (edge)
    board_edge = chess.Board(None)
    board_edge.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board_edge.set_piece_at(chess.A1, chess.Piece(chess.KNIGHT, chess.WHITE))
    board_edge.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    # Add the same pawns
    board_edge.set_piece_at(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
    board_edge.set_piece_at(chess.A7, chess.Piece(chess.PAWN, chess.BLACK))
    
    score_center = evaluate(board_center)
    score_edge = evaluate(board_edge)
    
    assert score_center > score_edge, f"Center knight should be better. Center: {score_center}, Edge: {score_edge}"
    print(f"Knight center vs edge test passed (Center: {score_center}, Edge: {score_edge})")


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
    # Create an actual stalemate position
    # King on a8, Queen on b6 (blocking), King on c6 - Black to move
    board = chess.Board(None)
    board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.B6, chess.Piece(chess.QUEEN, chess.WHITE))
    board.set_piece_at(chess.C6, chess.Piece(chess.KING, chess.WHITE))
    board.turn = chess.BLACK  # Black to move
    
    assert board.is_stalemate(), "Test position should be stalemate"
    
    score = evaluate(board)
    assert score == 0, f"Stalemate should be 0, got {score}"
    print("Stalemate test passed")


def test_pawn_advancement():
    """Advanced pawns should be valued higher than back-rank pawns"""
    # Pawn on 5th rank
    board_advanced = chess.Board(None)
    board_advanced.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board_advanced.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.WHITE))
    board_advanced.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    # Pawn on 2nd rank
    board_back = chess.Board(None)
    board_back.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board_back.set_piece_at(chess.E2, chess.Piece(chess.PAWN, chess.WHITE))
    board_back.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    score_advanced = evaluate(board_advanced)
    score_back = evaluate(board_back)
    
    assert score_advanced > score_back, f"Advanced pawn should be better. Advanced: {score_advanced}, Back: {score_back}"
    print("Pawn advancement test passed")


def test_endgame_detection():
    """Test endgame detection logic"""
    # Starting position - not endgame
    board = chess.Board()
    assert not is_endgame(board), "Starting position should not be endgame"
    
    # King and pawn endgame - should be endgame
    board_endgame = chess.Board(None)
    board_endgame.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board_endgame.set_piece_at(chess.E2, chess.Piece(chess.PAWN, chess.WHITE))
    board_endgame.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    board_endgame.set_piece_at(chess.E7, chess.Piece(chess.PAWN, chess.BLACK))
    assert is_endgame(board_endgame), "King and pawn should be endgame"
    
    print("Endgame detection test passed")


def test_king_safety_middlegame():
    """King should prefer safety in middlegame (castled position)"""
    # King castled kingside
    board_safe = chess.Board(None)
    board_safe.set_piece_at(chess.G1, chess.Piece(chess.KING, chess.WHITE))
    board_safe.set_piece_at(chess.F2, chess.Piece(chess.PAWN, chess.WHITE))
    board_safe.set_piece_at(chess.G2, chess.Piece(chess.PAWN, chess.WHITE))
    board_safe.set_piece_at(chess.H2, chess.Piece(chess.PAWN, chess.WHITE))
    board_safe.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    board_safe.set_piece_at(chess.D1, chess.Piece(chess.QUEEN, chess.WHITE))  # Queens on = middlegame
    board_safe.set_piece_at(chess.D8, chess.Piece(chess.QUEEN, chess.BLACK))
    
    # King exposed in center
    board_exposed = chess.Board(None)
    board_exposed.set_piece_at(chess.E4, chess.Piece(chess.KING, chess.WHITE))
    board_exposed.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    board_exposed.set_piece_at(chess.D1, chess.Piece(chess.QUEEN, chess.WHITE))
    board_exposed.set_piece_at(chess.D8, chess.Piece(chess.QUEEN, chess.BLACK))
    
    score_safe = evaluate(board_safe)
    score_exposed = evaluate(board_exposed)
    
    assert score_safe > score_exposed, f"Castled king should be safer in middlegame. Safe: {score_safe}, Exposed: {score_exposed}"
    print("King safety middlegame test passed")


def test_piece_square_symmetry():
    """Piece-square values should be symmetric for both colors"""
    # White knight on d4
    piece_white = chess.Piece(chess.KNIGHT, chess.WHITE)
    value_white = get_piece_square_value(piece_white, chess.D4)
    
    # Black knight on d5 (mirror position from Black's perspective)
    piece_black = chess.Piece(chess.KNIGHT, chess.BLACK)
    value_black = get_piece_square_value(piece_black, chess.D5)
    
    assert value_white == value_black, f"Piece-square values should be symmetric. White: {value_white}, Black: {value_black}"
    print("Piece-square symmetry test passed")


def test_doubled_pawns_penalty():
    """Doubled pawns should be penalized."""
    board = chess.Board(None)
    # White has doubled pawns on E file
    board.set_piece_at(chess.E2, chess.Piece(chess.PAWN, chess.WHITE))
    board.set_piece_at(chess.E3, chess.Piece(chess.PAWN, chess.WHITE))
    
    board.set_piece_at(chess.E7, chess.Piece(chess.PAWN, chess.BLACK))
    
    # Dummy Kings (needed if running full evaluate, but safe to include)
    board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.H1, chess.Piece(chess.KING, chess.WHITE))
    
    score = evaluate_pawns(board, chess.WHITE)
    assert score < 0, f"Doubled pawns should have negative score, got {score}"
    print(f"Doubled pawns penalty test passed (Score: {score})")

def test_isolated_pawn_penalty():
    """Isolated pawns should be penalized."""
    board = chess.Board(None)
    # White pawn on D4
    board.set_piece_at(chess.D4, chess.Piece(chess.PAWN, chess.WHITE))
    
    board.set_piece_at(chess.D7, chess.Piece(chess.PAWN, chess.BLACK))
    
    board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.H1, chess.Piece(chess.KING, chess.WHITE))
    
    score = evaluate_pawns(board, chess.WHITE)
    assert score < 0, f"Isolated pawn should have negative score, got {score}"
    print(f"Isolated pawn penalty test passed (Score: {score})")

def test_passed_pawn_bonus():
    """Passed pawns should receive a bonus."""
    board = chess.Board(None)
    # White pawn on E5
    board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.WHITE))
    
    # Black pawn on A7 (far away, does not block E5)
    board.set_piece_at(chess.A7, chess.Piece(chess.PAWN, chess.BLACK))
    
    board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.H1, chess.Piece(chess.KING, chess.WHITE))
    
    score = evaluate_pawns(board, chess.WHITE)
    assert score > 0, f"Passed pawn should have positive score, got {score}"
    print(f"Passed pawn bonus test passed (Score: {score})")

def run_new_tests():
    print("\n" + "="*50)
    print("Running New Pawn Structure Tests")
    print("="*50 + "\n")
    test_doubled_pawns_penalty()
    test_isolated_pawn_penalty()
    test_passed_pawn_bonus()
    print("\n" + "="*50)
    print("Pawn Tests Passed! ✓")
    print("="*50 + "\n")

def run_all_tests():
    """Run all test functions"""
    print("\n" + "="*50)
    print("Running Evaluation Tests (with Piece-Square Tables)")
    print("="*50 + "\n")
    
    test_starting_position()
    test_material_difference()
    test_black_up_queen()
    test_knight_center_vs_edge()
    test_checkmate_white_wins()
    test_checkmate_black_wins()
    test_stalemate()
    test_pawn_advancement()
    test_endgame_detection()
    test_king_safety_middlegame()
    test_piece_square_symmetry()
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()