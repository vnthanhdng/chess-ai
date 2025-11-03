from dataclasses import dataclass
import chess
from typing import List

@dataclass
class Puzzle:
    """Represents a chess puzzles.
    
    Attributes:
        puzzle_id: Unique identifier for the puzzle
        fen: FEN string representation the puzzle position
        moves: List of moves in UCI format (first move is the opponent's last move)
        rating: Difficulty rating of the puzzle
        rating_deviation: Uncertainty in the rating
        popularity: Popularity score of the puzzle
        nb_plays: Number of times the puzzle has been played
        themes: List of themes associated with the puzzle
        game_url: URL to the original game
    """
    puzzle_id: str
    fen: str
    moves: List[str]
    rating: int
    rating_deviation: int
    popularity: int
    nb_plays: int
    themes: List[str]
    game_url: str
    
    @property
    def solution_moves(self) -> List[str]:
        """Get the solution moves, minus the setup move.
        
        The first move in the moves list is the opponent's last move to set up the puzzle. 
        The remaining moves are the solution.
        
        Returns:
            List of solution moves in UCI format
        """
        return self.moves[1:] if len(self.moves) > 1 else []
    
    @property
    def first_solution_move(self) -> str:
        """Get the first move of the solution.
        
        Returns:
            The first solution move in UCI format
        """
        return self.solution_moves[0] if self.solution_moves else None
    
    @property
    def board(self) -> chess.Board:
        """Get the chess board for the puzzle position.
        
        Returns:
            chess.Board initialized to the puzzle's FEN position
        """
        board = chess.Board(self.fen)
        if self.moves:
            setup_move = chess.Move.from_uci(self.moves[0])
            board.push(setup_move)
        return board
    
    def has_theme(self, theme: str) -> bool:
        """Check if the puzzle has a specific theme.
        
        Args:
            theme: Theme to check

        Returns:
            True if the puzzle has the specified theme, False otherwise
        """
        return theme in self.themes
    
    def __str__(self) -> str:
        themes_str = ", ".join(self.themes[:3])
        return f"Puzzle {self.puzzle_id} (Rating: {self.rating}, Themes: {themes_str})"
    
    def __repr__(self) -> str:
        return f"Puzzle(puzzle_id={self.puzzle_id}, rating={self.rating}, themes={self.themes})"