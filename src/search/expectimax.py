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
        
        for move in moves:
            board.push(move)
            # Next node is Chance (opponent)
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
        self.nodes_searched += 1
        
        if board.is_game_over():
            return self.evaluator(board, ply_from_root)

        # 2. Quiescence at depth 0
        if depth == 0:
            # We determine if the board is 'stable' using rational exchanges
            # Pass the correct `maximizing` flag based on whose turn it is
            # relative to the agent color (board.turn == agent_color).
            return self._quiescence(board, float('-inf'), float('inf'), board.turn == agent_color, ply_from_root)
        
        # Chance node (Opponent)
        if is_chance_node:
            legal_moves = list(board.legal_moves)
            # No ordering needed for chance nodes (sum is commutative)
            
            total_eval = 0.0
            for move in legal_moves:
                board.push(move)
                # Next node is Optimal (Us)
                eval_score = self._expectimax(board, depth - 1, False, agent_color, ply_from_root + 1)
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
                    eval_score = self._expectimax(board, depth - 1, True, agent_color, ply_from_root + 1)
                    board.pop()
                    max_eval = max(max_eval, eval_score)
                return max_eval
            else: # Minimize
                min_eval = float('inf')
                for move in moves:
                    board.push(move)
                    eval_score = self._expectimax(board, depth - 1, True, agent_color, ply_from_root + 1)
                    board.pop()
                    min_eval = min(min_eval, eval_score)
                return min_eval

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, 
                   maximizing: bool, ply_from_root: int) -> float:
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
                score = self._quiescence(board, alpha, beta, False, ply_from_root + 1)
                board.pop()
                if score >= beta: return beta
                if score > alpha: alpha = score
            return alpha
        else:
            for move in capture_moves:
                board.push(move)
                score = self._quiescence(board, alpha, beta, True, ply_from_root + 1)
                board.pop()
                if score <= alpha: return alpha
                if score < beta: beta = score
            return beta

    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        return super()._order_moves(board, moves)
