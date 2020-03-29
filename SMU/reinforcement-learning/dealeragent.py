from abstractagent import AbstractAgent
from blackjack import BlackjackEnv, BlackjackObservation, BlackjackAction
from carddeck import *


class DealerAgent(AbstractAgent):
    """
    Implementation of an agent that plays the same strategy as the dealer.
    This means that the agent draws a card when sum of cards in his hand
    is less than 17.
    """

    def train(self):
        pass

    def get_action(self, observation: BlackjackObservation, terminal: bool) -> int:
        return BlackjackAction.HIT.value if observation.player_hand.value() < 17 else BlackjackAction.STAND.value
