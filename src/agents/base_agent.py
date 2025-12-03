"""Base class for chess agents."""

from abc import ABC, abstractmethod
import time
import chess
from typing import Optional, Dict, Any


class BaseAgent(ABC):
    """
    Abstract base class for all chess agents.
    
    All agents must implement the `choose_move` method, which selects
    a move for the given board position.
    
    Attributes:
        name: Human-readable name for the agent
        color: Chess color the agent plays (WHITE or BLACK)
        moves_made: Number of moves this agent has made
        nodes_searched: Total nodes searched (for search-based agents)
        total_time: Total computation time in seconds
    
    Example:
        >>> class RandomAgent(BaseAgent):
        ...     def choose_move(self, board, time_limit):
        ...         import random
        ...         return random.choice(list(board.legal_moves))
        >>> 
        >>> agent = RandomAgent(name="Random", color=chess.WHITE)
        >>> board = chess.Board()
        >>> move = agent.choose_move(board, time_limit=5.0)
    """
    
    def __init__(
        self, 
        name: str = "BaseAgent", 
        color: chess.Color = chess.BLACK
    ) -> None:
        """
        Initialize the agent.
        
        Args:
            name: Human-readable name for the agent
            color: Chess color the agent plays
        """
        self.name = name
        self.color = color
        
        # Statistics
        self.moves_made = 0
        self.nodes_searched = 0
        self.total_time = 0.0
    
    @abstractmethod
    def choose_move(
        self, 
        board: chess.Board, 
    ) -> Optional[chess.Move]:
        """
        Choose a move for the given board position.
        
        This method must be implemented by all subclasses.
        
        Args:
            board: Current board state
                
        Returns:
            The chosen move, or None if no legal moves available
        
        Note:
            Subclasses should update self.nodes_searched if applicable.
        """
        pass
    
    def select_move(
        self, 
        board: chess.Board, 
    ) -> Optional[chess.Move]:
        """
        Select a move with automatic timing and statistics tracking.
        
        This is the main entry point for getting a move from an agent.
        It wraps choose_move() with timing and statistics updates.
        
        Args:
            board: Current board state
        
        Returns:
            The chosen move, or None if no legal moves available
        """
        start_time = time.time()
        
        move = self.choose_move(board)
        
        elapsed = time.time() - start_time
        
        # Update statistics
        if move is not None:
            self.moves_made += 1
            self.total_time += elapsed
        
        return move
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for this agent.
        
        Returns:
            Dictionary with statistics including:
            - name: Agent name
            - color: Color playing
            - moves_made: Number of moves made
            - nodes_searched: Total nodes searched
            - total_time: Total computation time
            - avg_time_per_move: Average time per move
            - avg_nodes_per_move: Average nodes per move
        """
        avg_time = self.total_time / self.moves_made if self.moves_made > 0 else 0.0
        avg_nodes = self.nodes_searched / self.moves_made if self.moves_made > 0 else 0.0
        
        return {
            "name": self.name,
            "color": "White" if self.color == chess.WHITE else "Black",
            "moves_made": self.moves_made,
            "nodes_searched": self.nodes_searched,
            "total_time": round(self.total_time, 3),
            "avg_time_per_move": round(avg_time, 3),
            "avg_nodes_per_move": round(avg_nodes, 1),
        }
    
    def reset_stats(self) -> None:
        """Reset all performance statistics."""
        self.moves_made = 0
        self.nodes_searched = 0
        self.total_time = 0.0
    
    def __str__(self) -> str:
        """String representation of the agent."""
        color_str = "White" if self.color == chess.WHITE else "Black"
        return f"{self.name} ({color_str})"
    
    def __repr__(self) -> str:
        """Detailed representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', color={self.color})"
    
    def startEpisode():
        """Start training episode (Used by ReinforcementAgents to meter training episodes)."""
        pass

    def stopEpisode():
        """Stop training episode (Used by ReinforcementAgents to meter training episodes)."""
        pass


class RandomAgent(BaseAgent):
    """Agent that selects moves randomly."""
    
    def __init__(self, name: str = "RandomAgent", color: chess.Color = chess.BLACK):
        """Initialize Random agent.
        
        Args:
            name: Agent name
            color: Color the agent plays
        """
        super().__init__(name, color)
    
    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Choose a random legal move.
        
        Args:
            board: Current board state
            
        Returns:
            The chosen move, or None if no legal moves available
        """
        import random
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        return random.choice(legal_moves)

class SimpleAgent(BaseAgent):
    """Agent that selects the first legal move available."""
    
    def __init__(self, name: str = "SimpleAgent", color: chess.Color = chess.BLACK):
        """Initialize Simple agent.
        
        Args:
            name: Agent name
            color: Color the agent plays
        """
        super().__init__(name, color)
    
    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Choose the first legal move available.
        
        Args:
            board: Current board state
            
        Returns:
            The chosen move, or None if no legal moves available
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        return legal_moves[0]