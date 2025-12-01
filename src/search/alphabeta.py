"""Alpha-beta pruning search algorithm."""

import chess
from typing import Callable, List, Tuple, Optional
from .search_base import SearchAlgorithm

class AlphaBetaSearch(SearchAlgorithm):
    """
    Alpha-beta pruning with Move Ordering and Quiescence Search.
    """
    
    def __init__(self, evaluator: Callable[[chess.Board, int], int]):
        super().__init__(evaluator)
        # MVV-LVA (Most Valuable Victim - Least Valuable Aggressor) values
        # Used for move ordering
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
    
    def search(self, board: chess.Board, depth: int) -> Tuple[chess.Move, int]:
        self.reset_stats()
        best_move = None
        
        # Initial alpha/beta
        alpha = float('-inf')
        beta = float('inf')
        
        # Root level move ordering
        moves = self._order_moves(board, list(board.legal_moves))
        
        # We need to track best value to return correct move
        # Initialize based on whose turn it is
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')

        for move in moves:
            board.push(move)
            
            # Call recursive search
            eval_score = self._alpha_beta(
                board, 
                depth - 1, 
                alpha, 
                beta, 
                board.turn == chess.WHITE, 
                ply_from_root=1
            )
            
            board.pop()
            
            if board.turn == chess.WHITE:
                if eval_score > best_value:
                    best_value = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
            else:
                if eval_score < best_value:
                    best_value = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                
        return best_move, best_value

    def _alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                   maximizing: bool, ply_from_root: int) -> float:
        self.nodes_searched += 1
        
        if board.is_game_over():
            return self.evaluator(board, ply_from_root)

        # 1. Quiescence Search at Leaf Nodes
        # Instead of returning immediately at depth 0, we search captures until "quiet"
        if depth == 0:
            return self._quiescence(board, alpha, beta, maximizing, ply_from_root)

        # 2. Move Ordering
        # Generate moves and sort them so we search captures first
        moves = self._order_moves(board, list(board.legal_moves))

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                board.push(move)
                eval_score = self._alpha_beta(board, depth - 1, alpha, beta, False, ply_from_root + 1)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                board.push(move)
                eval_score = self._alpha_beta(board, depth - 1, alpha, beta, True, ply_from_root + 1)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break # Alpha cutoff
            return min_eval

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, 
                   maximizing: bool, ply_from_root: int) -> float:
        """
        Searches only capture moves to prevent the Horizon Effect.
        """
        self.nodes_searched += 1
        
        # 1. Stand Pat
        # Get a static evaluation of the current position
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

        # 2. Search only Captures
        # We only look at moves that capture pieces
        capture_moves = self._order_moves(board, [m for m in board.legal_moves if board.is_capture(m)])
        
        if maximizing:
            for move in capture_moves:
                board.push(move)
                score = self._quiescence(board, alpha, beta, False, ply_from_root + 1)
                board.pop()
                
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            return alpha
        else:
            for move in capture_moves:
                board.push(move)
                score = self._quiescence(board, alpha, beta, True, ply_from_root + 1)
                board.pop()
                
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
            return beta

    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """
        Sorts moves to improve pruning efficiency.
        Order:
        1. Captures (sorted by MVV-LVA: High val victim, Low val attacker)
        2. Promotions
        3. Quiet moves
        """
        def score_move(move):
            if board.is_capture(move):
                # MVV-LVA Logic
                attacker_piece = board.piece_at(move.from_square)
                victim_piece = board.piece_at(move.to_square)
                
                # En Passant handling
                if board.is_en_passant(move):
                    return 105 # Higher than pawn captures pawn
                
                attacker_val = self.piece_values.get(attacker_piece.piece_type, 0)
                victim_val = 0
                if victim_piece:
                    victim_val = self.piece_values.get(victim_piece.piece_type, 0)
                
                # Formula: Prioritize taking valuable pieces with cheap pieces
                return 10 * victim_val - attacker_val
                
            if move.promotion:
                return 900 # High priority
                
            return 0 # Quiet moves last

        return sorted(moves, key=score_move, reverse=True)