import evaluation
import sys
from collections import defaultdict
import random
from .learning_agent import ValueEstimationAgent
import chess
from utils import flipCoin
import concurrent.futures

class ValueIterationAgent(ValueEstimationAgent):
    """Value iteration agent."""
    def __init__(self, discount = 0.9, iterations = 3, name="ValueIterationAgent", color=chess.BLACK):
        """
        Initialize value iteration agent.

        Args:
            discount: discount factor for rewards
            iterations: Number of times value iteration should be run
            name: Name of agent
            color: Color agent plays
        """
        super().__init__(epsilon=0.1, name=name, color=color)
        self.discount = discount
        self.iterations = iterations
        self.values = defaultdict(float)
        self.states = self.getStates()
        self.newStates = set()
        self.runValueIteration()

    def _update_state(self, state):
        curBoard = chess.Board(state)
        curBoard.turn = chess.BLACK
        if evaluation.is_endgame(curBoard):
            return (state, 0)
        best_action = self.computeActionFromValues(curBoard)
        if not best_action:
            return (state, 0)
        else:
            return (state, self.computeQValueFromValues(curBoard, best_action))

    def runValueIteration(self):
        """Performs value iteration"""
        for _ in range(self.iterations):
            newVals = defaultdict(float)

            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = executor.map(self._update_state, self.states)

            for state, value in results:
                newVals[state] = value

            self.values = newVals
            self.states.update(self.newStates)
            self.newStates = set()

    def getStates(self) -> set[str]:
        """
        Get the initial states to create the value table.

        The initial states include a board with no moves, and any possible initial move.
        """
        states = set()
        board = chess.Board()
        for move in board.legal_moves:
            board.push(move)
            states.add(board.fen())
            board.pop()
        
        return states
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Get the chosen move by the agent.

        Args:
            board: The state of the board from which agent should make a move.
        """
        return self.computeActionFromValues(board)
    
    def getValue(self, state: str) -> float:
        """
            Return the value of the state (computed in __init__).

            Args:
                Fen string representation of board state to get the value for.
        """
        return self.values[state]


    def computeQValueFromValues(self, board: chess.Board, action: chess.Move):
        """
            Compute the Q-value of action in state from the value function stored in self.values.

            There is no transition state probability since chess is a deterministic game.
            The new state generated is added to the values table with 1% chance (chosen to minimize training time)

            Args:
                board: the current board state
                action: The move to compute QValue from.
        """
        board.push(action)
        board.turn = chess.WHITE if self.color == chess.BLACK else chess.BLACK
        opp_actions = list(board.legal_moves)
        # find the best value assuming opponent acts optimally
        if opp_actions:
            cur_values = []
            for move in opp_actions:
                board.push(move)
                if flipCoin(0.01): # with 1% probability add opponent state to states
                    self.newStates.add(board.fen())
                cur_values.append(self.getValue(board.fen()))
                board.pop()
            value = min(cur_values) if self.color == chess.BLACK else max(cur_values)
        else:
            value = self.getValue(board.fen())
        
        board.pop()
        return evaluation.evaluate(board) + self.discount*value

    def computeActionFromValues(self, board: chess.Board):
        """
        Determine best action based on board values.

        Args:
            board: The current chess board
        """
        if board.is_game_over():
            return None
        bestQ = float('inf') if self.color == chess.BLACK else float('-inf')
        bestActions = []
        for move in board.legal_moves:
            curQ = self.computeQValueFromValues(board, move)
            if curQ == bestQ:
                bestActions.append(move)
                continue
            if self.color == chess.BLACK:
                if curQ < bestQ:
                    bestQ = curQ
                    bestActions = [move]
            elif self.color == chess.WHITE:
                if curQ > bestQ:
                    bestQ = curQ
                    bestActions = [move] 

        return random.choice(bestActions)