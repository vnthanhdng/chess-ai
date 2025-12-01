"""Alpha-beta pruning search algorithm."""

import chess
from typing import Callable, List, Tuple, Optional
from .search_base import SearchAlgorithm

class AlphaBetaSearch(SearchAlgorithm):
    """
    Alpha-beta pruning with Move Ordering and Quiescence Search.
    """
    
    def __init__(self, evaluator: Callable[[chess.Board, int], int]):
        super().__init__(evaluator)
        # MVV-LVA (Most Valuable Victim - Least Valuable Aggressor) values
        # Used for move ordering
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
    
    def search(self, board: chess.Board, depth: int) -> Tuple[chess.Move, int]:
        self.reset_stats()
        best_move = None
        
        # Initial alpha/beta
        alpha = float('-inf')
        beta = float('inf')
        
        # Root level move ordering
        moves = self._order_moves(board, list(board.legal_moves))
        
        # We need to track best value to return correct move
        # Initialize based on whose turn it is
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')

        # Path-based repetition detection
        root_key = board.transposition_key() if hasattr(board, "transposition_key") else board.fen()
        path_keys = {root_key}

        for move in moves:
            board.push(move)
            eval_score = self._alpha_beta(
                board,
                depth - 1,
                alpha,
                beta,
                board.turn == chess.WHITE,
                ply_from_root=1,
                path_keys=path_keys,
            )
            board.pop()
            
            if board.turn == chess.WHITE:
                if eval_score > best_value:
                    best_value = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
            else:
                if eval_score < best_value:
                    best_value = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                
        return best_move, best_value

    def _alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                   maximizing: bool, ply_from_root: int, path_keys: set) -> float:
        self.nodes_searched += 1
        # Repetition detection / path management: add current key and remove on return
        key = board.transposition_key() if hasattr(board, "transposition_key") else board.fen()
        if key in path_keys:
            return 0

        path_keys.add(key)
        try:
            if board.is_game_over():
                return self.evaluator(board, ply_from_root)

            # 1. Quiescence Search at Leaf Nodes
            # Instead of returning immediately at depth 0, we search captures until "quiet"
            if depth == 0:
                return self._quiescence(board, alpha, beta, maximizing, ply_from_root, path_keys)

            # 2. Move Ordering
            # Generate moves and sort them so we search captures first
            moves = self._order_moves(board, list(board.legal_moves))

            if maximizing:
                max_eval = float('-inf')
                for move in moves:
                    board.push(move)
                    eval_score = self._alpha_beta(board, depth - 1, alpha, beta, False, ply_from_root + 1, path_keys)
                    board.pop()

                    max_eval = max(max_eval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break # Beta cutoff
                return max_eval
            else:
                min_eval = float('inf')
                for move in moves:
                    board.push(move)
                    eval_score = self._alpha_beta(board, depth - 1, alpha, beta, True, ply_from_root + 1, path_keys)
                    board.pop()

                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break # Alpha cutoff
                return min_eval
        finally:
            path_keys.remove(key)
