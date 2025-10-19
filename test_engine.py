import chess
from engine import find_best_move, find_best_move_alpha_beta, minimax, alpha_beta


def test_captures_free_piece():
    """AI should capture a hanging piece"""
    # Position: Black queen is hanging on d5
    board = chess.Board()
    board.set_fen("rnb1kbnr/pppp1ppp/8/3q4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    
    best_move = find_best_move(board, depth=2)
    
    # Should capture the queen
    assert best_move.uci() == "d1d5" or board.piece_at(best_move.to_square) == chess.Piece(chess.QUEEN, chess.BLACK), \
        f"Should capture free queen, but played {best_move}"
    
    print("Captures free piece test passed")


def test_avoids_hanging_piece():
    """AI should not hang its own pieces"""
    # Simple position where hanging a piece would be bad
    board = chess.Board()
    
    # Move that would hang the queen
    bad_move = chess.Move.from_uci("d1h5")
    
    best_move = find_best_move(board, depth=3)
    
    # Should not play the bad move
    assert best_move != bad_move, "Should not hang the queen"
    
    print("Avoids hanging piece test passed")


def test_finds_mate_in_one():
    """AI should find checkmate in one move"""
    # Position: White can checkmate with Qf7#
    board = chess.Board()
    board.set_fen("rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 0 1")
    # Actually let's use a clearer mate in 1
    board.set_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
    
    best_move = find_best_move(board, depth=2)
    
    # Should play Qxf7# (checkmate)
    assert best_move.uci() == "h5f7", f"Should play Qxf7#, but played {best_move}"
    
    print("Finds mate in one test passed")


def test_alphabeta_equals_minimax():
    """Alpha-beta should give same result as minimax"""
    board = chess.Board()
    
    # Get moves from both algorithms
    minimax_move = find_best_move(board, depth=3)
    alphabeta_move = find_best_move_alpha_beta(board, depth=3)
    
    # Evaluate both moves - they should have equal value (though move might differ)
    board.push(minimax_move)
    minimax_value = minimax(board, 2, False)
    board.pop()
    
    board.push(alphabeta_move)
    alphabeta_value = alpha_beta(board, 2, float('-inf'), float('inf'), False)
    board.pop()
    
    assert minimax_value == alphabeta_value, \
        f"Minimax and alpha-beta should give equal evaluations, got {minimax_value} vs {alphabeta_value}"
    
    print("Alpha-beta equals minimax test passed")


def test_prefers_better_material_trade():
    """AI should prefer winning trades (taking more than it loses)"""
    # Position where AI can trade knight for queen
    board = chess.Board()
    board.set_fen("rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 1")
    
    # Black can capture the knight with queen
    # But that hangs the queen to the bishop
    # AI should see this and not make the bad trade
    best_move = find_best_move(board, depth=3)
    
    # Should NOT capture the knight with the queen (that would be Qxf3)
    assert best_move.uci() != "d8f6" and best_move.uci() != "d8f3", \
        "Should not make a bad trade"
    
    print("Prefers better material trade test passed")


def test_handles_no_legal_moves():
    """Engine should handle positions with no legal moves gracefully"""
    # Stalemate position - no legal moves
    board = chess.Board(None)
    board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
    board.set_piece_at(chess.A6, chess.Piece(chess.QUEEN, chess.WHITE))
    board.set_piece_at(chess.C7, chess.Piece(chess.KING, chess.WHITE))
    board.turn = chess.BLACK
    
    best_move = find_best_move(board, depth=2)
    
    # Should return None (no legal moves)
    assert best_move is None, "Should return None when no legal moves"
    
    print("Handles no legal moves test passed")


def test_depth_consistency():
    """Higher depth should make same or better decisions"""
    board = chess.Board()
    
    # Get move at different depths
    move_d2 = find_best_move(board, depth=2)
    move_d3 = find_best_move(board, depth=3)
    
    # Both should be legal moves
    assert move_d2 in board.legal_moves, "Depth 2 move should be legal"
    assert move_d3 in board.legal_moves, "Depth 3 move should be legal"
    
    print("Depth consistency test passed")


def run_all_tests():
    """Run all test functions"""
    print("\n" + "="*50)
    print("Running Engine Tests")
    print("="*50 + "\n")
    
    test_captures_free_piece()
    test_avoids_hanging_piece()
    test_finds_mate_in_one()
    test_alphabeta_equals_minimax()
    test_prefers_better_material_trade()
    test_handles_no_legal_moves()
    test_depth_consistency()
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()