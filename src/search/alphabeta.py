"""Alpha-beta pruning search algorithm."""

import chess
from typing import Callable
from .search_base import SearchAlgorithm


class AlphaBetaSearch(SearchAlgorithm):
    """Alpha-beta pruning search algorithm implementation."""
    
    def __init__(self, evaluator: Callable[[chess.Board, int], int]):
        """
        Initialize alpha-beta search.
        
        Args:
            evaluator: Function that evaluates a board position
                      Should accept (board, ply_from_root) parameters
        """
        super().__init__(evaluator)
    
    def search(self, board: chess.Board, depth: int) -> tuple[chess.Move, int]:
        """
        Search for the best move using alpha-beta pruning.
        
        Args:
            board: Current board position
            depth: Search depth in plies
            
        Returns:
            tuple: (best_move, evaluation_score)
        """
        self.reset_stats()
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in board.legal_moves:
            board.push(move)
            # Pass ply_from_root=1 since we're one ply from root
            move_value = self._alpha_beta(board, depth - 1, alpha, beta, board.turn == chess.WHITE, ply_from_root=1)
            board.pop()

            if board.turn == chess.WHITE:
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
                alpha = max(alpha, move_value)
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move
                beta = min(beta, move_value)

        return best_move, best_value
    
    def _alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool, ply_from_root: int) -> float:
        """
        Alpha-beta pruning recursive implementation.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player
            ply_from_root: Number of plies from the root position
            
        Returns:
            float: Evaluation score
        """
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            # Pass ply_from_root to evaluator for mate distance scoring
            return self.evaluator(board, ply_from_root)

        if maximizing:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self._alpha_beta(board, depth - 1, alpha, beta, False, ply_from_root + 1)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self._alpha_beta(board, depth - 1, alpha, beta, True, ply_from_root + 1)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval