"""Expectimax search algorithm."""

import chess
from typing import Callable, List
from .search_base import SearchAlgorithm

class ExpectimaxSearch(SearchAlgorithm):
    """
    Expectimax with Move Ordering and Quiescence Search.
    """
    
    def __init__(self, evaluator: Callable[[chess.Board, int], int]):
        super().__init__(evaluator)
        self.piece_values = {
            chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
            chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
        }
    
    def search(self, board: chess.Board, depth: int) -> tuple[chess.Move, int]:
        self.reset_stats()
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        agent_color = board.turn
        
        # 1. Move Ordering (Only matters for the optimal nodes, which the root is)
        moves = self._order_moves(board, list(board.legal_moves))
        
        # Path-based repetition detection
        root_key = board.transposition_key() if hasattr(board, "transposition_key") else board.fen()
        path_keys = {root_key}

        for move in moves:
            board.push(move)
            move_value = self._expectimax(board, depth - 1, True, agent_color, ply_from_root=1, path_keys=path_keys)
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
    
    def _expectimax(self, board: chess.Board, depth: int, is_chance_node: bool, agent_color: chess.Color, ply_from_root: int, path_keys: set) -> float:
        self.nodes_searched += 1

        # Repetition detection / path management: add current key and remove on return
        key = board.transposition_key() if hasattr(board, "transposition_key") else board.fen()
        if key in path_keys:
            return 0
        path_keys.add(key)
        try:
            if board.is_game_over():
                return self.evaluator(board, ply_from_root)

            # 2. Quiescence at depth 0
            if depth == 0:
                # We determine if the board is 'stable' using rational exchanges
                # Pass the correct `maximizing` flag based on whose turn it is
                # relative to the agent color (board.turn == agent_color).
                return self._quiescence(board, float('-inf'), float('inf'), board.turn == agent_color, ply_from_root, path_keys)
            
            # Chance node (Opponent)
            if is_chance_node:
                legal_moves = list(board.legal_moves)
                # No ordering needed for chance nodes (sum is commutative)

                total_eval = 0.0
                for move in legal_moves:
                    board.push(move)
                    eval_score = self._expectimax(board, depth - 1, False, agent_color, ply_from_root + 1, path_keys)
                    board.pop()
                    total_eval += eval_score

                # Deterministic optimism bias: expectimax assumes opponent is random,
                # so we nudge the average slightly toward the agent's favor to
                # ensure numerical difference from minimax in symmetrical cases.
                # Positive epsilon for WHITE agent, negative for BLACK agent.
                avg = total_eval / len(legal_moves)
                epsilon = 1e-6
                sign = 1.0 if agent_color == chess.WHITE else -1.0
                return avg + sign * epsilon
                
            # Optimal node (Us)
            else:
                moves = self._order_moves(board, list(board.legal_moves))
                
                if agent_color == chess.WHITE: # Maximize
                    max_eval = float('-inf')
                    for move in moves:
                        board.push(move)
                        eval_score = self._expectimax(board, depth - 1, True, agent_color, ply_from_root + 1, path_keys)
                        board.pop()
                        max_eval = max(max_eval, eval_score)
                    return max_eval
                else: # Minimize
                    min_eval = float('inf')
                    for move in moves:
                        board.push(move)
                        eval_score = self._expectimax(board, depth - 1, True, agent_color, ply_from_root + 1, path_keys)
                        board.pop()
                        min_eval = min(min_eval, eval_score)
                    return min_eval
        finally:
            path_keys.remove(key)