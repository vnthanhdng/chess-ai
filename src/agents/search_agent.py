from .base_agent import BaseAgent
from ..search import SearchAlgorithm, MiniMaxSearch, AlphaBetaSearch, ExpectimaxSearch
import chess

class SearchAgent(BaseAgent):
    """Agent that uses a search algorithm to select moves."""
    
    def __init__(self, search_algorithm: SearchAlgorithm, depth: int = 3, name: str = "SearchAgent", color: chess.Color = chess.BLACK):
        """Initialize search-based agent.
        
        Args: 
            search_algorithm: Search algo instance
            depth: Search depth in plies
            name: Agent name
            color: Color the agent plays
        """
        super().__init__(name, color)
        self.search = search_algorithm
        self.depth = depth
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        """Choose a move using the search algorithm.
        
        Args:
            board: Current board state
            
        Returns:
            The chosen move
        """
        move, eval_score = self.search.search(board, self.depth)
        self.nodes_searched += self.search.nodes_searched
        return move
    
    def get_search_info(self) -> dict:
        """Get search statistics.
        
        Returns:
            Dictionary with search statistics
        """
        return {
            "depth": self.depth,
            "nodes_searched": self.search.nodes_searched,
            "algorithm": type(self.search).__name__
        }
        
class MinimaxAgent(SearchAgent):
    """Agent that uses Minimax search algorithm."""
    
    def __init__(self, evaluator, depth: int = 3, name: str = "MinimaxAgent", color: chess.Color = chess.BLACK):
        """Initialize Minimax agent.
        
        Args:
            evaluator: Board evaluation function
            depth: Search depth in plies
            name: Agent name
            color: Color the agent plays
        """
        search_algorithm = MiniMaxSearch(evaluator)
        super().__init__(search_algorithm, depth, name, color)
        
class AlphaBetaAgent(SearchAgent):
    """Agent that uses Alpha-Beta pruning search algorithm."""
    
    def __init__(self, evaluator, depth: int = 3, name: str = "AlphaBetaAgent", color: chess.Color = chess.BLACK):
        """Initialize Alpha-Beta agent.
        
        Args:
            evaluator: Board evaluation function
            depth: Search depth in plies
            name: Agent name
            color: Color the agent plays
        """
        search_algorithm = AlphaBetaSearch(evaluator)
        super().__init__(search_algorithm, depth, name, color)

class ExpectimaxAgent(SearchAgent):
    """Agent that uses Expectimax search algorithm."""
    
    def __init__(self, evaluator, depth: int = 3, name: str = "ExpectimaxAgent", color: chess.Color = chess.BLACK):
        """Initialize Expectimax agent.
        
        Args:
            evaluator: Board evaluation function
            depth: Search depth in plies
            name: Agent name
            color: Color the agent plays
        """
        search_algorithm = ExpectimaxSearch(evaluator)
        super().__init__(search_algorithm, depth, name, color)