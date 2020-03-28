import numpy as np

from abstractagent import AbstractAgent
from blackjack import BlackjackEnv, BlackjackObservation, BlackjackAction
from state import State, StateMap


class SarsaAgent(AbstractAgent):
    """
    Here you will provide your implementation of SARSA method.
    You are supposed to implement train() method. If you want
    to, you can split the code in two phases - training and
    testing, but it is not a requirement.

    For SARSA explanation check AIMA book or Sutton and Burton
    book. You can choose any strategy and/or step-size function
    (learning rate) as long as you fulfil convergence criteria.
    """

    def __init__(self, env: BlackjackEnv, number_of_epochs: int, eps: float = 10000, alpha: float = 100,
                 gamma: float = 0.9, verbose: bool = False):
        super().__init__(env, number_of_epochs, verbose=verbose)
        self.num_actions = len(BlackjackAction)
        sa1 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_NUM_STATES, self.num_actions))
        sa2 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_ONE_CARD_NUM_STATES, State.HAS_ACE_NUM_STATES,
                        self.num_actions))
        q1 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_NUM_STATES, self.num_actions))
        q2 = np.zeros((State.PLAYER_NUM_STATES, State.DEALER_ONE_CARD_NUM_STATES, State.HAS_ACE_NUM_STATES,
                       self.num_actions))
        self.sa_counter = StateMap(np.zeros(self.num_actions), sa1, sa2)
        self.q = StateMap(np.zeros(self.num_actions), q1, q2)
        self.eps = eps
        self.alpha = alpha
        self.gamma = gamma

    def get_action(self, state_idx):
        action = np.argmax(self.q[state_idx])
        return action

    def _get_train_action(self, state_idx, n):
        if np.random.rand() > self._eps_f(n):
            return self.get_action(state_idx)
        else:
            return np.random.randint(self.num_actions)

    def _alpha_f(self, n) -> float:
        return self.alpha / (self.alpha - 1 + n)

    def _eps_f(self, n) -> float:
        # k = self.eps / (0.9 * self.number_of_epochs)
        # eps = self.eps - k * n
        # return eps if eps >= 0 else 0
        return self.eps / (self.eps - 1 + n)

    def _update_q(self, state: State, action: int, reward: int, next_state: State, next_action: int):
        state_idx = state.state_index_with_action(action)
        next_state_idx = next_state.state_index_with_action(next_action)
        self.sa_counter[state_idx] += 1
        self.q[state_idx] = self.q[state_idx] + self._alpha_f(self.sa_counter[state_idx]) * (
                reward + self.gamma * self.q[next_state_idx] - self.q[state_idx])

    def train(self):
        for n in range(self.number_of_epochs):
            print(n)
            observation = self.env.reset()
            self._render_game()
            state = State.obs_to_state(observation)
            terminal = False
            action = self._get_train_action(state.state_index(), n)
            # action = action.value
            while not terminal:
                next_observation, reward, terminal, _ = self.env.step(action)
                self._render_game()
                next_state = State.obs_to_state(next_observation)
                next_action = self._get_train_action(next_state.state_index(), n)
                self._update_q(state, action, reward, next_state, next_action)
                state, action = next_state, next_action

    def get_hypothesis(self, observation: BlackjackObservation, terminal: bool, action: int) -> float:
        """
        Implement this method so that I can test your code. This method is supposed to return your learned Q value for
        particular observation and action.

        :param observation: The observation as in the game. Contains information about what the player sees - player's
        hand and dealer's hand.
        :param terminal: Whether the hands were seen after the end of the game, i.e. whether the state is terminal.
        :param action: Action for Q-value.
        :return: The learned Q-value for the given observation and action.
        """
        state = State.obs_to_state(observation)
        return self.q[state.state_index_with_action(action)]

    def __str__(self):
        q_table = self.q[2, :]
        argm = np.argmax(q_table, 3)
        argm = (q_table[:, :, :, 0] != q_table[:, :, :, 1]) * (argm + 1)
        out = ""
        row_format = "{:>10}" + "{:>7}" + "{:>5}" * (State.DEALER_ONE_CARD_NUM_STATES - 1) + '\n'
        header = [x + 2 for x in range(State.DEALER_ONE_CARD_NUM_STATES)]
        width = 10 + 7 + 5 * (State.DEALER_ONE_CARD_NUM_STATES - 1)
        out += " ACTIONS IF AGENT DOESN'T HAVE ACE ".center(width, "*") + '\n' + row_format.format("Hand value",
                                                                                                   *header) + '\n'
        for player_state in range(State.PLAYER_NUM_STATES):
            actions = ['S' if x == 1 else 'H' if x == 2 else '-' for x in argm[player_state, :, 0]]
            out += row_format.format(player_state + 4, *actions)
        out += '\n'
        out += " ACTIONS IF AGENT HAS ACE ".center(width, "*") + '\n' + row_format.format("Hand value", *header) + '\n'
        for player_state in range(State.PLAYER_NUM_STATES):
            actions = ['S' if x == 1 else 'H' if x == 2 else '-' for x in argm[player_state, :, 1]]
            out += row_format.format(player_state + 4, *actions)
        return out

    def save(self, path='sarsa'):
        self.q.save(path, 'q')
        self.sa_counter.save(path, 'sa_counter')

    def load(self, path='sarsa'):
        self.q = StateMap.load(path, 'q')
        self.sa_counter = StateMap.load(path, 'sa_counter')
