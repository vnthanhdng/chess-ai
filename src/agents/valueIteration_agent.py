import evaluation
import sys
from collections import defaultdict

from .learning_agent import ValueEstimationAgent
import chess
from utils import flipCoin

"""
Consider using no mdp, there's a way to get legal moves and then use the search to determine the most probable action...

there is no way to determine states:
when the user uses the rl agent, it is essentially in the eval phase
in the training phase it should be playing by itself?
how? how to get states which are potential spaces in the board AND furthermore, how to get the probabilities for these?
I think using an equal probability to start (ie naive solution) is the best way to start...
"""

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, discount = 0.9, iterations = 3):
        """
          todo: update the new states thing, its hacky
        """
        self.name = "ValueIterationAgent"
        self.discount = discount
        self.iterations = iterations
        self.values = defaultdict(float)
        self.states = self.getStates()
        self.newStates = set()
        self.epsilon = 0.1
        self.runValueIteration()

    def runValueIteration(self):
        for _ in range(self.iterations):
            newVals = defaultdict(float)
            for state in self.states:
                curBoard = chess.Board(state)
                curBoard.turn = chess.BLACK
                if evaluation.is_endgame(curBoard):
                    continue
                best_action = self.computeActionFromValues(curBoard)
                if not best_action:
                    newVals[state] = 0
                else:
                    newVals[state] = self.computeQValueFromValues(curBoard, best_action)

            self.values = newVals
            self.states.update(self.newStates)
            self.newStates = set()
            print(len(self.states))
    
    def get_search_info(self):
        pass

    def getStates(self) -> set[str]:
        """Just gets the initial state space which consists of starting moves.
        For now, assume your agent is black, no white...
        """
        states = set()
        board = chess.Board()
        for move in board.legal_moves:
            board.push(move)
            states.add(board.fen())
            board.pop()
        
        return states
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        return self.computeActionFromValues(board)
    
    def getValue(self, state: str) -> float:
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, curBoard: chess.Board, action: chess.Move):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.

          note: this is flawed because the reward is based only on the next state, not the action
          There is no transition state probability since chess is a deterministic game

          this updates the list of possible states since the statespace is hard to determine
          explicitly
        """
        curBoard.push(action)
        curBoard.turn = chess.WHITE
        opp_actions = list(curBoard.legal_moves)
        if not opp_actions:
            value = self.getValue(curBoard.fen())
        else:
            value = float('inf')
            # find the estimated value of next state given opponent acts optimally
            for move in opp_actions:
                curBoard.push(move)
                if flipCoin(0.001):
                    self.newStates.add(curBoard.fen())
                value = min(value, self.getValue(curBoard.fen()))
                curBoard.pop()
        curBoard.pop()
        return evaluation.evaluate(curBoard) + self.discount*value

    def computeActionFromValues(self, board: chess.Board):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        if evaluation.is_endgame(board):
            return None
        minQ = sys.maxsize
        minAction = None
        for move in board.legal_moves:
            curQ = self.computeQValueFromValues(board, move)
            if curQ < minQ:
                minQ = curQ
                minAction = move

        return minAction