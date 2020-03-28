from abstractagent import AbstractAgent
from blackjack import BlackjackEnv, BlackjackObservation
from carddeck import *


class RandomAgent(AbstractAgent):
    """
    Implementation of an agent that decides completely at random.
    """

    def train(self):
        for i in range(self.number_of_epochs):
            print(i)
            observation = self.env.reset()
            terminal = False
            reward = 0
            while not terminal:
                self.env.render() # you may want to see the game actually being played
                action = self.make_step(observation, reward, terminal)
                observation, reward, terminal, _ = self.env.step(action)
            self.env.render()

    def make_step(self, observation: BlackjackObservation, reward: float, terminal: bool) -> int:
        return self.env.action_space.sample()
