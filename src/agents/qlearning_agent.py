"""QLearning Agent."""

from .learning_agent import ReinforcementAgent
from collections import defaultdict
import random
import chess
from utils import flipCoin
from evaluation import evaluate

class QLearningAgent(ReinforcementAgent):
    """Q-Learning Agent."""
    def __init__(self, **args):
        ReinforcementAgent.__init__(self, **args)
        self.q_values = defaultdict(float)
        self.train()
    
    def train(self):
        """
        Train a QLearning agent against an opponent making random moves
        """
        for _ in range(self.numTraining):
            board = chess.Board()
            self.startEpisode()
            while not board.is_game_over():
                if board.turn == self.color:
                    state = board.copy()
                    action = self.getAction(state)
                    self.doAction(state, action)
                    board.push(action)
                else:
                    opp_moves = list(board.legal_moves)
                    if opp_moves:
                        board.push(random.choice(opp_moves))
            self.final(board)


    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Determine best move based on current board state and QValues.
        
        Args:
            board: The chess board to get the move for.
        
        Returns:
            chess.Move: The move QLearningAgent decides upon
        """
        # initiate start of episode
        action = self.getAction(board)
        self.doAction(board, action)
        return action
    

    def doAction(self,state: chess.Board, action:chess.Move):
        """
            Called by inherited class when
            an action is taken in a state
        """
        self.lastState = state
        self.lastAction = action

        nextState = self.lastState.copy()
        nextState.push(action)
        reward = evaluate(nextState) - evaluate(state)
        self.observeTransition(state, action, nextState, reward)


    def getQValue(self, board: chess.Board, action: chess.Move) -> float:
        """
            Returns the Qvalue for a given state and action

            Should return 0.0 if we have never seen a state
            or the Q node value otherwise

        Args:
            board: The board to get the value for
            action: The move to take from the state
        """
        return self.q_values[(board.fen(), action)]


    def computeValueFromQValues(self, board: chess.Board) -> float:
        """
            Returns the highest value from the given board. Minimizes values if color is black, otherwise maximize.

            Args:
                board: The state from which to return the best value
        """
        if board.is_game_over() or not board.legal_moves:
            return 0.0
        
        values = []
        for move in board.legal_moves:
            board.push(move)
            values.append(self.getQValue(board, move))
            board.pop()
        
        return min(values) if self.color == chess.BLACK else max(values)
    

    def computeActionFromQValues(self, board: chess.Board) -> chess.Move:
        """
            Compute the best action to take in a state (Minimizes if color is black, maximizes otherwise).

            Args:
                board: The state from which to return the best action
        """
        board.turn = self.color
        if board.is_game_over() or not board.legal_moves:
            return None

        bestVal = float('inf') if self.color == chess.BLACK else float('-inf')
        bestMoves = []
        for move in board.legal_moves:
            board.push(move)
            curVal = self.getQValue(board, move)
            board.pop()
            if curVal == bestVal:
                bestMoves.append(move)
            if curVal < bestVal and self.color == chess.BLACK: 
                bestVal = curVal
                bestMoves = [move]
            elif curVal > bestVal and self.color == chess.WHITE:
                bestVal = curVal
                bestMoves = [move]
        
        return random.choice(bestMoves)

    def getAction(self, board: chess.Board) -> chess.Move:
        """
            Compute the action to take in the current state. 

            Args:
                board: the state from which the best action should be chosen.
        """
        # Pick Action
        board.turn = self.color
        action = None
        if flipCoin(self.epsilon):
            action = random.choice(list(board.legal_moves))
        else:
            action = self.computeActionFromQValues(board)

        return action
    
    def final(self, board: chess.Board):
        """
        Called after episode

        Args:
            The ending state of the board
        """
        deltaReward = evaluate(board) - evaluate(self.lastState)
        self.observeTransition(self.lastState, self.lastAction, board, deltaReward)
        self.stopEpisode()

    def registerInitialState(self, board: chess.Board):
        """Start training."""
        self.startEpisode()

    def update(self, board: chess.Board, action: chess.Move, nextBoard: chess.Board, reward: int):
        """
            Performs state update
            
            state = action => nextState and reward transition.

            Args:
                board: The current state of the board
                action: The chosen action to 
                nextBoard: The board state after performing the action
                reward: The reward for the action taken

        """
        sample = reward + self.discount*self.computeValueFromQValues(nextBoard)
        self.q_values[(board.fen(), action)] = (1-self.alpha)*self.getQValue(board, action)+self.alpha*sample