"""Expectimax search algorithm."""

import chess
from typing import Callable
from .search_base import SearchAlgorithm


class ExpectimaxSearch(SearchAlgorithm):
    """Expectimax search algorithm implementation."""
    
    def __init__(self, evaluator: Callable[[chess.Board, int], int]):
        """
        Initialize expectimax search.
        
        Args:
            evaluator: Function that evaluates a board position
                      Should accept (board, ply_from_root) parameters
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
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        agent_color = board.turn
        
        for move in board.legal_moves:
            board.push(move)
            # Pass ply_from_root=1 since we're one ply from root
            move_value = self._expectimax(board, depth - 1, True, agent_color, ply_from_root=1)
            board.pop()
            
            if agent_color == chess.WHITE:
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move
        
        return best_move, best_value
    
    def _expectimax(self, board: chess.Board, depth: int, is_chance_node: bool, agent_color: chess.Color, ply_from_root: int) -> float:
        """
        Expectimax recursive implementation.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            is_chance_node: True if this is a chance node (opponent's turn), 
                           False if this is an optimal node (our turn)
            agent_color: The color of the player we're optimizing for
            ply_from_root: Number of plies from the root position
            
        Returns:
            float: Evaluation score
        """
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            # Pass ply_from_root to evaluator for mate distance scoring
            return self.evaluator(board, ply_from_root)
        
        # chance node — assume random play
        if is_chance_node:
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                return self.evaluator(board, ply_from_root)
            
            total_eval = 0.0
            for move in legal_moves:
                board.push(move)
                eval_score = self._expectimax(board, depth - 1, False, agent_color, ply_from_root + 1)
                board.pop()
                total_eval += eval_score
            
            return total_eval / len(legal_moves)
        # optimal node
        else:
            if agent_color == chess.WHITE: # white - maximize
                max_eval = float('-inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval_score = self._expectimax(board, depth - 1, True, agent_color, ply_from_root + 1)
                    board.pop()
                    max_eval = max(max_eval, eval_score)
                return max_eval
            else: # black - minimize
                min_eval = float('inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval_score = self._expectimax(board, depth - 1, True, agent_color, ply_from_root + 1)
                    board.pop()
                    min_eval = min(min_eval, eval_score)
                return min_eval