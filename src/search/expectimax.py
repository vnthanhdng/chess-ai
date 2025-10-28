"""Expectimax search algorithm."""

import chess
from typing import Callable
from .search_base import SearchAlgorithm


class ExpectimaxSearch(SearchAlgorithm):
    """Expectimax search algorithm implementation."""
    
    def __init__(self, evaluator: Callable[[chess.Board], int]):
        """
        Initialize expectimax search.
        
        Args:
            evaluator: Function that evaluates a board position
        """
        super().__init__(evaluator)
    
    def search(self, board: chess.Board, depth: int) -> tuple[chess.Move, int]:
        """
        Search for the best move using expectimax.
        
        Args:
            board: Current board position
            depth: Search depth in plies
            
        Returns:
            tuple: (best_move, evaluation_score)
        """
        self.reset_stats()
        best_move = None
        best_value = float('-inf')
        
        for move in board.legal_moves:
            board.push(move)
            # After our move, opponent's turn is a chance node
            move_value = self._expectimax(board, depth - 1, False)
            board.pop()
            
            if move_value > best_value:
                best_value = move_value
                best_move = move
        
        return best_move, best_value
    
    def _expectimax(self, board: chess.Board, depth: int, is_max_node: bool) -> float:
        """
        Expectimax recursive implementation.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            is_max_node: True if this is a maximizing node (our turn), 
                        False if chance node (opponent's turn)
            
        Returns:
            float: Evaluation score
        """
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            return self.evaluator(board)
        
        if is_max_node:
            # Maximizing node: choose the best move
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score = self._expectimax(board, depth - 1, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            # Chance node: take average of all possible moves
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                return self.evaluator(board)
            
            total_eval = 0.0
            for move in legal_moves:
                board.push(move)
                eval_score = self._expectimax(board, depth - 1, True)
                board.pop()
                total_eval += eval_score
            
            return total_eval / len(legal_moves)

