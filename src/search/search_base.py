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

    # Default piece values used for MVV-LVA if subclass doesn't provide one
    DEFAULT_PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000,
    }

    def _order_moves(self, board: chess.Board, moves: list, *, for_chance: bool = False, for_quiescence: bool = False) -> list:
        """Default move ordering (MVV-LVA + promotions + light penalties).

        Args:
            board: current board
            moves: iterable of moves to order
            for_chance: if True, ordering is light (cheap) because chance
                        nodes average outcomes and ordering has less impact
            for_quiescence: if True, ordering is tuned for quiescence (captures)
        """
        # Delegate to central scoring helper which may be overridden or
        # customized. Keep the sorting stable and inexpensive.
        moves_list = list(moves)
        moves_list.sort(key=lambda m: self._score_move(board, m, for_chance=for_chance, for_quiescence=for_quiescence), reverse=True)
        return moves_list

    def _score_move(self, board: chess.Board, move: chess.Move, *, for_chance: bool = False, for_quiescence: bool = False) -> int:
        """Score a single move for ordering.

        This central helper implements MVV-LVA, promotion handling, and
        light heuristics to avoid immediate back-and-forth (ping-pong)
        moves and to discourage king shuffles.
        """
        piece_values = getattr(self, 'piece_values', self.DEFAULT_PIECE_VALUES)

        # Captures: MVV-LVA with en-passant handling
        if board.is_capture(move):
            attacker = board.piece_at(move.from_square)
            victim = board.piece_at(move.to_square)

            if board.is_en_passant(move):
                base = 105
            else:
                val_a = piece_values.get(attacker.piece_type, 0) if attacker else 0
                val_v = piece_values.get(victim.piece_type, 0) if victim else 0
                base = 10 * val_v - val_a

            # Stronger penalty for immediate back-and-forth repetitions
            last_move = board.move_stack[-1] if board.move_stack else None
            if last_move and move.from_square == last_move.to_square and move.to_square == last_move.from_square:
                base -= 200

            # Penalize king captures/shuffles more strongly to avoid meaningless king moves
            if attacker and attacker.piece_type == chess.KING:
                base -= 60

            return base

        # Promotions are very valuable
        if move.promotion:
            return 900

        # Quiet moves: small bonuses for pawn pushes, penalties for king moves
        mover = board.piece_at(move.from_square)
        score = 0
        if mover and mover.piece_type == chess.PAWN:
            score += 5
        if mover and mover.piece_type == chess.KING:
            score -= 20

        # If this ordering is for chance nodes, keep it cheap
        if for_chance:
            return score

        return score

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, maximizing: bool, ply_from_root: int, path_keys: set) -> float:
        """Default quiescence search: search captures until quiet.

        Accepts `path_keys` to avoid cycles on the current search path.
        """
        self.nodes_searched += 1

        # Repetition check for quiescence children
        key = board.transposition_key() if hasattr(board, 'transposition_key') else board.fen()
        if key in path_keys:
            return 0

        path_keys.add(key)
        try:
            stand_pat = self.evaluator(board, ply_from_root)

            if maximizing:
                if stand_pat >= beta:
                    return beta
                if stand_pat > alpha:
                    alpha = stand_pat
            else:
                if stand_pat <= alpha:
                    return alpha
                if stand_pat < beta:
                    beta = stand_pat

            # Only consider capture moves in quiescence
            capture_moves = self._order_moves(board, [m for m in board.legal_moves if board.is_capture(m)], for_quiescence=True)

            if maximizing:
                for move in capture_moves:
                    board.push(move)
                    child_key = board.transposition_key() if hasattr(board, 'transposition_key') else board.fen()
                    if child_key in path_keys:
                        score = 0
                    else:
                        path_keys.add(child_key)
                        score = self._quiescence(board, alpha, beta, False, ply_from_root + 1, path_keys)
                        path_keys.remove(child_key)
                    board.pop()
                    if score >= beta:
                        return beta
                    if score > alpha:
                        alpha = score
                return alpha
            else:
                for move in capture_moves:
                    board.push(move)
                    child_key = board.transposition_key() if hasattr(board, 'transposition_key') else board.fen()
                    if child_key in path_keys:
                        score = 0
                    else:
                        path_keys.add(child_key)
                        score = self._quiescence(board, alpha, beta, True, ply_from_root + 1, path_keys)
                        path_keys.remove(child_key)
                    board.pop()
                    if score <= alpha:
                        return alpha
                    if score < beta:
                        beta = score
                return beta
        finally:
            path_keys.remove(key)