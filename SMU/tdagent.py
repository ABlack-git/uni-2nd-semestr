import numpy as np
from abstractagent import AbstractAgent
from blackjack import BlackjackObservation, BlackjackEnv, BlackjackAction
from state import State


class TDAgent(AbstractAgent):
    """
    Implementation of an agent that plays the same strategy as the dealer.
    This means that the agent draws a card when sum of cards in his hand
    is less than 17.

    Your goal is to modify train() method to learn the state utility function
    and the get_hypothesis() method that returns the state utility function.
    I.e. you need to change this agent to a passive reinforcement learning
    agent that learns utility estimates using temporal difference method.
    """

    def __init__(self, env: BlackjackEnv, number_of_epochs: int, alpha: float = 2, gamma: float = 0.5,
                 verbose: bool = False):
        super().__init__(env, number_of_epochs, verbose=verbose)
        self.state_freq = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_NUM_STATES, State.HAS_ACE_NUM_STATES))
        self.state_util = np.empty((State.PLAYER_NUM_STATES, State.DEALER_NUM_STATES, State.HAS_ACE_NUM_STATES))
        self.state_util.fill(np.nan)
        self.last_state_idx = None
        self.last_reward = 0
        self.alpha = alpha
        self.gamma = gamma

    def train(self):
        for i in range(self.number_of_epochs):
            print(i)
            observation = self.env.reset()
            self.update_agent_state(State.obs_to_state(observation), 0, False)
            terminal = False
            while not terminal:
                self._render_game()
                action = self.receive_observation_and_get_action(observation, terminal)
                observation, reward, terminal, _ = self.env.step(action)
                state = State.obs_to_state(observation)
                self.update_agent_state(state, reward, terminal)
            self._render_game()

    def update_agent_state(self, state, reward, terminal):
        state_idx = state.state_index()
        if self.last_state_idx is not None:
            self._update_utility(state_idx, reward)

        if np.isnan(self.state_util[state_idx]):
            self.state_util[state_idx] = reward

        self.state_freq[state_idx] += 1
        if terminal:
            self.last_state_idx = None
            self.last_reward = 0
        else:
            self.last_state_idx = state_idx
            self.last_reward = reward

    def adaptive_alpha(self, n):
        return self.alpha / (self.alpha - 1 + n)

    def _update_utility(self, state_idx, reward):
        self.state_util[self.last_state_idx] += self.adaptive_alpha(self.state_freq[state_idx]) * (
                    reward + self.gamma * self.state_util[state_idx] - self.state_util[self.last_state_idx])

    def receive_observation_and_get_action(self, observation: BlackjackObservation, terminal: bool) -> int:
        return BlackjackAction.HIT.value if observation.player_hand.value() < 17 else BlackjackAction.STAND.value

    def get_hypothesis(self, observation: BlackjackObservation, terminal: bool) -> float:
        """
        Implement this method so that I can test your code. This method is supposed to return your learned U value for
        particular observation.

        :param observation: The observation as in the game. Contains information about what the player sees - player's
        hand and dealer's hand.
        :param terminal: Whether the hands were seen after the end of the game, i.e. whether the state is terminal.
        :return: The learned U-value for the given observation.
        """
        return self.state_util[State.obs_to_state(observation).state_index()]
