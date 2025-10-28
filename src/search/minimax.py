"""Minimax search algorithm."""

import chess
from typing import Callable
from .search_base import SearchAlgorithm

class MiniMaxSearch(SearchAlgorithm):
    """Minimax search algorithm implementation."""
    
    def __init__(self, evaluator: Callable[[chess.Board], int]):
        """
        Initalize minimax search.
        
        Args:
            evaluator: Function that evaluates the board state.
        """
        super().__init__(evaluator)
    
    def search(self, board: chess.Board, depth: int) -> tuple[chess.Move, int]:
        """
        Search for the best move using minimax.
        
        Args:
            board: Current board position
            depth: Search depth in plies
            
        Returns:
            tuple: (best_move, evaluation_score)
        """
        self.reset_stats()
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            move_value = self._minimax(board, depth - 1, board.turn == chess.WHITE)
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
    
    def _minimax(self, board: chess.Board, depth: int, maximizing: bool) -> int:
        """
        Minimax recursive implementation.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            maximizing: True if maximizing player
            
        Returns:
            int: Evaluation score
        """
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            return self.evaluator(board)
        
        if maximizing:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, False)
                board.pop()
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, True)
                board.pop()
                min_eval = min(min_eval, eval)
            return min_eval