from .base_agent import BaseAgent
import chess
from typing import Optional


class HumanAgent(BaseAgent):
    """
    A human agent that prompts for input via the console.
    
    This agent is designed to work with interactive game loops
    where human input is collected separately.
    """
    
    def __init__(self, name: str = "Human", color: chess.Color = chess.WHITE) -> None:
        """
        Initialize human agent.
        
        Args:
            name: Player name
            color: Color to play
        """
        super().__init__(name, color)
    
    def choose_move(
        self, 
        board: chess.Board, 
    ) -> Optional[chess.Move]:
        """
        Get move from human input.
        
        Args:
            board: Current board state
        
        Returns:
            The move entered by the human, or None if quitting
        """
        return self._get_human_input(board)
    
    def _get_human_input(
        self, 
        board: chess.Board, 
    ) -> Optional[chess.Move]:
        """
        Prompt human for move input.
        
        Args:
            board: Current board state
        
        Returns:
            Parsed move or None
        """
        while True:
            
            print("Enter move (e.g., 'e2e4' or 'Nf3'), 'help' for commands:")
            user_input = input("> ").strip().lower()
            
            # Handle commands
            if user_input in ['quit', 'exit']:
                return None
            
            if user_input == 'help':
                self._print_help(board)
                continue
            
            if user_input == 'moves':
                self._print_legal_moves(board)
                continue
            
            # Try to parse move
            try:
                # Try UCI format (e2e4)
                if len(user_input) in [4, 5]:
                    move = chess.Move.from_uci(user_input)
                else:
                    # Try SAN format (Nf3, e4)
                    move = board.parse_san(user_input)
                
                if move in board.legal_moves:
                    return move
                else:
                    print("Illegal move. Try again.")
            
            except (ValueError, chess.InvalidMoveError, chess.IllegalMoveError):
                print("Invalid move format. Try 'e2e4' or 'Nf3'")
    
    def _print_help(self, board: chess.Board) -> None:
        """Print help information."""
        print("\n" + "="*50)
        print("COMMANDS:")
        print("  • Enter moves: 'e2e4' (UCI) or 'Nf3' (SAN)")
        print("  • 'moves'  - Show all legal moves")
        print("  • 'help'   - Show this help")
        print("  • 'quit'   - Exit game")
        print("="*50 + "\n")
    
    def _print_legal_moves(self, board: chess.Board) -> None:
        """Print all legal moves."""
        moves = [board.san(move) for move in board.legal_moves]
        print(f"\nLegal moves ({len(moves)}):")
        for i in range(0, len(moves), 8):
            print("  " + ", ".join(moves[i:i+8]))
        print()