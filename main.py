# Game loop

import chess
from engine import find_best_move

board = chess.Board()
while not board.is_game_over():
    print(board)
    move = find_best_move(board, depth=3)
    board.push(move)
