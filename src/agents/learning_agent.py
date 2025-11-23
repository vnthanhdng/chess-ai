"""Base classes for Learning agents (Value iteration, Q-learning)."""

from .base_agent import BaseAgent
import chess
from abc import abstractmethod

class ValueEstimationAgent(BaseAgent):
    """
      V(s) = max_{a in actions} Q(s,a)
      policy(s) = arg_max_{a in actions} Q(s,a)
    """
    def __init__(self, alpha=1.0, epsilon=0.05, gamma=0.8, numTraining = 10, name="ValueEstimationAgent", color:chess.Color = chess.BLACK):
        """
        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        super().__init__(name, color)
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.discount = float(gamma)
        self.numTraining = int(numTraining)
    
    def get_search_info(self):
        pass

class ReinforcementAgent(ValueEstimationAgent):
    """
      Abstract Reinforcemnt Agent: Q-Learning agents should inherit
    """
    @abstractmethod
    def update(self, board, action, nextState, reward):
        """
                This class will call this function, which you write, after
                observing a transition and reward
        """
        raise NotImplementedError

    def getLegalActions(self,board):
        """
          Get the actions available for a given
          state.
        """
        return board.legal_moves

    def observeTransition(self, board, action, nextState, deltaReward):
        """
            Called by environment to inform agent that a transition has
            been observed. This will result in a call to self.update
            on the same arguments
        """
        self.episodeRewards += deltaReward
        self.update(board, action, nextState, deltaReward)
    
    def doAction(self,state,action):
        """
            Called by inherited class when
            an action is taken in a state
        """
        self.lastState = state
        self.lastAction = action

    def startEpisode(self):
        """
          Start training episode
        """
        self.lastState = None
        self.lastAction = None
        self.episodeRewards = 0.0

    def stopEpisode(self):
        """
          Stop training episode
        """
        if self.episodesSoFar < self.numTraining:
            self.accumTrainRewards += self.episodeRewards
        else:
            self.accumTestRewards += self.episodeRewards
        self.episodesSoFar += 1
        if self.episodesSoFar >= self.numTraining:
            # Take off the training wheels
            self.epsilon = 0.0    # no exploration
            self.alpha = 0.0      # no learning
    
    def isInTraining(self):
        return self.episodesSoFar < self.numTraining

    def isInTesting(self):
        return not self.isInTraining()

    def __init__(self, numTraining=100, epsilon=0.5, alpha=0.5, gamma=1,  name="ReinforcementAgent", color:chess.Color = chess.BLACK):
        """
        actionFn: Function which takes a state and returns the list of legal actions

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        super().__init__(alpha, epsilon, gamma, numTraining, name, color)
        self.episodesSoFar = 0
        self.accumTrainRewards = 0.0
        self.accumTestRewards = 0.0
