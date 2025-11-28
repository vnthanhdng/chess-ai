"""Minimax search algorithm."""

import chess
from typing import Callable, List
from .search_base import SearchAlgorithm

class MiniMaxSearch(SearchAlgorithm):
    """
    Minimax with Move Ordering and Quiescence Search.
    """
    
    def __init__(self, evaluator: Callable[[chess.Board, int], int]):
        super().__init__(evaluator)
        # MVV-LVA Values for Move Ordering
        self.piece_values = {
            chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
            chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
        }
    
    def search(self, board: chess.Board, depth: int) -> tuple[chess.Move, int]:
        self.reset_stats()
        best_move = None
        # Initialize best_value depending on whose turn it is
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        
        # 1. Order moves to check promising ones first
        moves = self._order_moves(board, list(board.legal_moves))
        
        for move in moves:
            board.push(move)
            # Pass ply_from_root=1
            move_value = self._minimax(board, depth - 1, board.turn == chess.WHITE, ply_from_root=1)
            board.pop()
            
            if board.turn == chess.WHITE:
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move
        
        return best_move, best_value
    
    def _minimax(self, board: chess.Board, depth: int, maximizing: bool, ply_from_root: int) -> int:
        self.nodes_searched += 1
        
        if board.is_game_over():
            return self.evaluator(board, ply_from_root)

        # 2. Quiescence Search at Leaf Nodes
        # Prevents the Horizon Effect
        if depth == 0:
            # We use local alpha/beta for quiescence to keep it fast
            return self._quiescence(board, float('-inf'), float('inf'), maximizing, ply_from_root)
        
        # 3. Move Ordering in Recursive steps
        moves = self._order_moves(board, list(board.legal_moves))

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, False, ply_from_root + 1)
                board.pop()
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, True, ply_from_root + 1)
                board.pop()
                min_eval = min(min_eval, eval)
            return min_eval

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, 
                   maximizing: bool, ply_from_root: int) -> float:
        self.nodes_searched += 1
        
        stand_pat = self.evaluator(board, ply_from_root)
        
        if maximizing:
            if stand_pat >= beta: return beta
            if stand_pat > alpha: alpha = stand_pat
        else:
            if stand_pat <= alpha: return alpha
            if stand_pat < beta: beta = stand_pat

        # Search only captures
        capture_moves = self._order_moves(board, [m for m in board.legal_moves if board.is_capture(m)])
        
        if maximizing:
            for move in capture_moves:
                board.push(move)
                score = self._quiescence(board, alpha, beta, False, ply_from_root + 1)
                board.pop()
                if score >= beta: return beta
                if score > alpha: alpha = score
            return alpha
        else:
            for move in capture_moves:
                board.push(move)
                score = self._quiescence(board, alpha, beta, True, ply_from_root + 1)
                board.pop()
                if score <= alpha: return alpha
                if score < beta: beta = score
            return beta

    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        def score_move(move):
            if board.is_capture(move):
                attacker = board.piece_at(move.from_square)
                victim = board.piece_at(move.to_square)
                if board.is_en_passant(move): return 105
                val_a = self.piece_values.get(attacker.piece_type, 0)
                val_v = self.piece_values.get(victim.piece_type, 0) if victim else 0
                return 10 * val_v - val_a
            if move.promotion: return 900
            return 0
        return sorted(moves, key=score_move, reverse=True)