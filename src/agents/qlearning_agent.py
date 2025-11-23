from learning_agent import ReinforcementAgent
from collections import defaultdict
import random
import chess
from utils import flipCoin
from evaluation import evaluate

class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent
      to do the training, we just create a maximizer, for any given new state,
      we just find the move that will maximize the score and that is our self play agent action
      then the next state etc. 

    """
    def __init__(self, **args):
        ReinforcementAgent.__init__(self, **args)
        self.q_values = defaultdict(float)

    def choose_move(self, board: chess.Board) -> chess.Move:
        return self.computeActionFromQValues(board)

    def getQValue(self, state: str, action: chess.Move):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        return self.q_values[(state, action)]


    def computeValueFromQValues(self, board: chess.Board):
        """
          Returns max_action Q(state,action)
          since ai is black, we want to minmize total score
        """
        if board.is_game_over() or not board.legal_moves:
            return 0.0
        minVal = float("inf")
        for move in board.legal_moves:
            board.push(move)
            minVal = min(minVal, self.getQValue(board.fen(), move))
            board.pop()
        
        return minVal
    

    def computeActionFromQValues(self, board: chess.Board):
        """
          Compute the best action to take in a state.
        """
        if board.is_game_over() or not board.legal_moves:
            return None

        minVal = float("inf")
        bestMoves = []
        for move in board.legal_moves:
            board.push(move)
            curVal = self.getQValue(board.fen(), move)
            board.pop()
            if curVal < minVal:
                minVal = curVal
                bestMoves = [move]
            elif curVal == minVal:
                bestMoves.append(move)
        
        return random.choice(bestMoves)

    def getAction(self, state):
        """
          Compute the action to take in the current state.  
        """
        # Pick Action
        board = chess.Board(state)
        action = None
        if flipCoin(self.epsilon):
            action = random.choice(board.legal_moves)
        else:
            action = self.computeActionFromQValues(board)

        return action
    
    def final(self, state):
        """
        Called after episode
        """
        deltaReward = evaluate(chess.Board(state)) - evaluate(chess.Board(self.lastState))
        self.observeTransition(self.lastState, self.lastAction, state, deltaReward)
        self.stopEpisode()

    def registerInitialState(self, state):
        """Start training"""
        self.startEpisode()

    def update(self, state, action, nextState, reward):
        """
          state = action => nextState and reward transition.
          You should do your Q-Value update here
        """
        sample = reward + self.discount*self.computeValueFromQValues(nextState)
        self.q_values[(state, action)] = (1-self.alpha)*self.getQValue(state, action)+self.alpha*sample