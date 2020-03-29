from abc import ABC, abstractmethod
from blackjack import BlackjackEnv, BlackjackObservation


class AbstractAgent(ABC):
    """
    Abstract base class for agents in the homework. Provides two fields: env for the environment and number_of_epochs.
    """

    def __init__(self, env: BlackjackEnv, number_of_epochs: int, verbose: bool = False):
        """
        Initializes the agent.
        :param env: The environment in which the agent plays Blackjack.
        :param number_of_epochs: Number of epochs to train on.
        """
        self.env = env
        self.number_of_epochs = number_of_epochs
        self.verbose = verbose
        super().__init__()

    @abstractmethod
    def train(self):
        """
        This method should train the agent by repeatedly playing the game.
        :return: None.
        """
        pass

    def get_action(self, observation: BlackjackObservation, terminal: bool) -> int:
        pass

    def test(self):
        for i in range(self.number_of_epochs):
            print(i, flush=True)
            observation = self.env.reset()
            terminal = False
            reward = 0
            self._render_game()
            while not terminal:
                action = self.get_action(observation, terminal)
                observation, reward, terminal, _ = self.env.step(action)
                self._render_game()

    def _render_game(self):
        if self.verbose:
            self.env.render()
