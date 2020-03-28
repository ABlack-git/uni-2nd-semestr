import numpy as np
from abstractagent import AbstractAgent
from blackjack import BlackjackObservation, BlackjackEnv, BlackjackAction
from state import State, StateMap


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

    def __init__(self, env: BlackjackEnv, number_of_epochs: int, alpha: float = 100, gamma: float = 0.9,
                 verbose: bool = False):
        super().__init__(env, number_of_epochs, verbose=verbose)
        sf1 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_NUM_STATES))
        sf2 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_ONE_CARD_NUM_STATES, State.HAS_ACE_NUM_STATES))
        su1 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_NUM_STATES))
        su2 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_ONE_CARD_NUM_STATES, State.HAS_ACE_NUM_STATES))

        self.state_freq = StateMap(0, sf1, sf2)
        self.state_util = StateMap(0, su1, su2)
        self.alpha = alpha
        self.gamma = gamma

    def train(self):
        for i in range(self.number_of_epochs):
            print(i)
            observation = self.env.reset()
            self._render_game()
            terminal = False
            while not terminal:
                action = self.receive_observation_and_get_action(observation, terminal)
                next_observation, reward, terminal, _ = self.env.step(action)
                self._render_game()
                state = State.obs_to_state(observation)
                next_state = State.obs_to_state(next_observation)
                self._update_utility(state, next_state, reward)
                observation = next_observation

    def alpha_f(self, n):
        return self.alpha / (self.alpha - 1 + n)

    def _update_utility(self, state: State, next_state: State, reward: int):
        state_idx = state.state_index()
        next_state_idx = next_state.state_index()
        self.state_freq[state_idx] += 1
        self.state_util[state_idx] = self.state_util[state_idx] + self.alpha_f(self.state_freq[state_idx]) * (
                reward + self.gamma * self.state_util[next_state_idx] - self.state_util[state_idx])

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

    def save(self, path='tdagent'):
        self.state_freq.save(path, 'state_freq')
        self.state_util.save(path, 'state_util')

    def load(self, path='tdagent'):
        self.state_freq = StateMap.load(path, 'state_freq')
        self.state_util = StateMap.load(path, 'state_util')

    def __str__(self):
        state_util = self.state_util.array[2]
        out = ""
        row_format = "{:>10}" + "{:>10}" + "{:>8}" * (State.DEALER_ONE_CARD_NUM_STATES - 1) + '\n'
        header = [x + 2 for x in range(State.DEALER_ONE_CARD_NUM_STATES)]
        width = 10 + 10 + 8 * (State.DEALER_ONE_CARD_NUM_STATES - 1)
        out += " UTILITY IF AGENT DOESN'T HAVE ACE ".center(width, "*") + '\n' + row_format.format("Hand value",
                                                                                                   *header) + '\n'
        for player_state in range(State.PLAYER_NUM_STATES):
            util = [f"{x:.3f}" for x in state_util[player_state, :, 0]]
            out += row_format.format(player_state + 4, *util)
        out += '\n'
        out += " UTILITY IF AGENT HAS ACE ".center(width, "*") + '\n' + row_format.format("Hand value", *header) + '\n'
        for player_state in range(State.PLAYER_NUM_STATES):
            util = [f'{x:.3f}' for x in state_util[player_state, :, 1]]
            out += row_format.format(player_state + 4, *util)
        return out
