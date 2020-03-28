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
        for i in range(self.number_of_epochs):
            print(i)
            observation = self.env.reset()
            terminal = False
            reward = 0
            while not terminal:
                # self.env.render()
                action = self.make_step(observation, reward, terminal)
                observation, reward, terminal, _ = self.env.step(action)
            # self.env.render()

    def make_step(self, observation: BlackjackObservation, reward: float, terminal: bool) -> int:
        return BlackjackAction.HIT.value if observation.player_hand.value() < 17 else BlackjackAction.STAND.value
