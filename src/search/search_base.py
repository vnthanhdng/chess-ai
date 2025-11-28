from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple
import inspect
import chess


class SearchAlgorithm(ABC):
    """Abstract base class for search algorithms."""

    def __init__(self, evaluator: Callable, ply_from_root: int = 0):
        """Initialize search algorithm.

        Args:
            evaluator: Function that evaluates a board position and returns
                       an integer score. Signature: `evaluator(board, ply)`.
            ply_from_root: Number of plies already performed from the root
                           (used by some algorithms to adjust evaluation).
        """
        # Normalize evaluator to a function taking (board, ply_from_root)
        # Many existing evaluators accept only (board), so wrap those to
        # ignore the ply argument. Use inspect to detect the callable's
        # signature and adapt accordingly.
        try:
            sig = inspect.signature(evaluator)
            params = sig.parameters
            # If evaluator accepts at least 2 positional args or *args, keep as-is
            accepts_two = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params.values())
            if not accepts_two:
                # Count only positional-or-keyword parameters
                pos_params = [p for p in params.values() if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)]
                if len(pos_params) >= 2:
                    accepts_two = True

            if accepts_two:
                self.evaluator = evaluator
            else:
                # Wrap single-arg evaluator to accept (board, ply)
                def _wrapped(board: chess.Board, ply: int = 0) -> int:
                    return evaluator(board)
                self.evaluator = _wrapped
        except (TypeError, ValueError):
            # If signature inspection fails, fall back to calling with both
            # arguments and let Python raise if it's incompatible.
            self.evaluator = evaluator
        self.nodes_searched = 0
        self.ply_from_root = ply_from_root

    @abstractmethod
    def search(self, board: chess.Board, depth: int) -> Tuple[Optional[chess.Move], int]:
        """
        Search for the best move.

        Args:
            board: Current board position
            depth: Search depth in plies

        Returns:
            Tuple of `(best_move, evaluation_score)`. `best_move` may be
            `None` if no legal moves are available (e.g., checkmate/stalemate).
        """
        raise NotImplementedError()

    def reset_stats(self):
        """Reset search statistics."""
        self.nodes_searched = 0