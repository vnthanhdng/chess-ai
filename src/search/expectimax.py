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

                return total_eval / len(legal_moves)
                
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

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, 
                   maximizing: bool, ply_from_root: int, path_keys: set) -> float:
        """
        Helper to determine stable board value using rational exchanges.
        """
        self.nodes_searched += 1
        
        stand_pat = self.evaluator(board, ply_from_root)
        
        if maximizing:
            if stand_pat >= beta: return beta
            if stand_pat > alpha: alpha = stand_pat
        else:
            if stand_pat <= alpha: return alpha
            if stand_pat < beta: beta = stand_pat

        capture_moves = self._order_moves(board, [m for m in board.legal_moves if board.is_capture(m)])
        
        if maximizing:
            for move in capture_moves:
                board.push(move)
                child_key = board.transposition_key() if hasattr(board, "transposition_key") else board.fen()
                if child_key in path_keys:
                    score = 0
                else:
                    path_keys.add(child_key)
                    score = self._quiescence(board, alpha, beta, False, ply_from_root + 1, path_keys)
                    path_keys.remove(child_key)
                board.pop()
                if score >= beta: return beta
                if score > alpha: alpha = score
            return alpha
        else:
            for move in capture_moves:
                board.push(move)
                child_key = board.transposition_key() if hasattr(board, "transposition_key") else board.fen()
                if child_key in path_keys:
                    score = 0
                else:
                    path_keys.add(child_key)
                    score = self._quiescence(board, alpha, beta, True, ply_from_root + 1, path_keys)
                    path_keys.remove(child_key)
                board.pop()
                if score <= alpha: return alpha
                if score < beta: beta = score
            return beta

    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        def score_move(move):
            if board.is_capture(move):
                attacker = board.piece_at(move.from_square)
                victim = board.piece_at(move.to_square)
                if board.is_en_passant(move): return 105
                val_a = self.piece_values.get(attacker.piece_type, 0)
                val_v = self.piece_values.get(victim.piece_type, 0) if victim else 0
                score = 10 * val_v - val_a
                # Penalize immediate back-and-forth repetitions
                last_move = board.move_stack[-1] if board.move_stack else None
                if last_move and move.from_square == last_move.to_square and move.to_square == last_move.from_square:
                    score -= 100
                # Penalize king shuffles
                if attacker and attacker.piece_type == chess.KING:
                    score -= 30
                return score
            if move.promotion: return 900
            # Small penalty for quiet king moves
            mover = board.piece_at(move.from_square)
            if mover and mover.piece_type == chess.KING:
                return -10
            return 0
        return sorted(moves, key=score_move, reverse=True)