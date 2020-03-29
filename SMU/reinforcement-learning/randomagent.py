from abstractagent import AbstractAgent
from blackjack import BlackjackEnv, BlackjackObservation
from carddeck import *


class RandomAgent(AbstractAgent):
    """
    Implementation of an agent that decides completely at random.
    """

    def train(self):
        pass

    def get_action(self, observation: BlackjackObservation, terminal: bool):
        return self.env.action_space.sample()
