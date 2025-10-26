from abc import ABC, abstractmethod
from typing import Callable
import chess

class SearchAlgorithm(ABC):
    """Abstract base class for search algorithms."""
    
    def __init__(self, evaluator: Callable[[chess.Board], int]):
        """Initalize search algorithm.
        
        Args:
            evaluator: Function that evaluates a board position.
        """
        self.evaluator = evaluator
        self.nodes_searched = 0
    
    @abstractmethod
    def search(self, board: chess.Board, depth: int) -> tuple[chess.Move, int]:
        """
        Search for the best move.
        
        Args:
            board: Current board position
            depth: Search depth in plies
        
        Returns:
            tuple: (best move, evaluation score)
        """
        pass

    def reset_stats(self):
        """Reset search statistics."""
        self.nodes_searched = 0
    
    